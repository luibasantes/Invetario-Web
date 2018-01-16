from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .forms import CreateOriginalPostForm, CreateThreadForm
from .models import Post,Thread
from django.urls import reverse
from django.http import Http404
from django.core.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PostSerializer

# Create your views here.
def index(request):

	username = request.user
	return render(request,"Foro/index.html",{'usuario':username})
		

def anuncios(request):
	all_anuncios = Thread.objects.filter(category="anuncio",op__aprobado=True).order_by("-id")
	username = request.user
	moderador = request.user.userprofile.moderador
	context = {'usuario':username,"anuncios":all_anuncios,"moderador":moderador}
	return render(request, "Foro/anuncios.html", context)
	
#Vista detallada de cada Post
def detalle_anuncio(request,Post_Id):
	form_Post = CreateOriginalPostForm(request.POST or None,request.FILES or None)
	try:
		post = Post.objects.get(id = str(Post_Id))
		thread = Thread.objects.get(op=post)
		respuestas = Post.objects.filter(reply_to = str(Post_Id),aprobado = True)
	except Post.DoesNotExist:
		raise Http404("Anuncio no existe")
	except Thread.DoesNotExist:
		raise Http404("Anuncio no es OP	")
		
	if 	form_Post.is_valid():
		my_Post = form_Post.save(commit=False)
		my_Post.reply_to = Post.objects.get(id = str(Post_Id))
		my_Post.owner = request.user
		my_Post.save()
		thread.save()
		form_Post = CreateOriginalPostForm(request.POST or None,request.FILES or None)
		contenido={"anuncio":post,'thread':thread,'usuario':request.user,'respuestas':respuestas,'form':form_Post}	
		return render(request,"foro/hilo.html",contenido)
	contenido={"anuncio":post,'thread':thread,'usuario':request.user,'respuestas':respuestas,'form':form_Post}	
	return render(request,"foro/hilo.html",contenido)
	
	
def create_anuncio(request):
	form_Thread = CreateThreadForm(request.POST or None)
	form_Post = CreateOriginalPostForm(request.POST or None,request.FILES or None)
	if form_Thread.is_valid() and form_Post.is_valid():
		my_Post = form_Post.save(commit=False)
		my_Post.owner = request.user
		my_Post.save()
		my_thread = form_Thread.save(commit=False)
		my_thread.category ='anuncio'
		my_thread.op =Post.objects.last()
		my_thread.save()
		return redirect(reverse('foro:anuncios'))
	context = {'user_form': form_Thread, 'profile_form': form_Post,'usuario':request.user}
	return render(request, 'Foro/create_anuncio.html', context)

def galeria(request):
	username = request.user
	info = dict()
	posts = Post.objects.all()
	for post in posts:
		if post.aprobado:
			if post.image:
				if post.reply_to:
					info[post] = Thread.objects.get(op=post.reply_to)
				else:
					info[post] = Thread.objects.get(op=post)
	return render(request,"Foro/galeria.html", {'usuario':username, 'info':info})
	
def hilo(request):
	username = request.user
	return render(request,"Foro/hilo.html", {'usuario':username})

def mapa(request):
	username = request.user
	return render(request, "Foro/mapa.html", {'usuario':username})

def timeline(request):
	username = request.user
	return render(request, "Foro/fechas.html", {'usuario': username})

def moderacion(request):
	username = request.user
	return render(request, "Foro/panel.html", {'usuario':username})

def acerca_de(request):
	admins = []
	username = request.user
	staff = User.objects.filter(is_staff=True)
	return render(request, "Foro/acercaDe.html", {'usuario':username, 'staff':staff})

def aprobar(request):
	username = request.user
	if not (username.userprofile.moderador):
		raise PermissionDenied
	posts = Post.objects.filter(aprobado=None).order_by("-id")
	if len(posts) > 0:
		return render(request, "Foro/aprobar.html", {'usuario':username,'posts':posts, 'titulo':"Posts por aprobar"})
	else:
		return render(request, "Foro/aprobar.html", {'usuario': username, 'titulo': "No hay posts por aprobar"})

def rechazados(request):
	username = request.user
	if not (username.userprofile.moderador or username.is_staff):
		return PermissionDenied
	posts = Post.objects.filter(aprobado=False)
	if len(posts) > 0:
		return render(request, "Foro/aprobar.html", {'usuario':username,'posts':posts, 'titulo':"Posts Rechazados / Eliminados"})
	else:
		return render(request, "Foro/aprobar.html", {'usuario': username, 'titulo': "No hay posts Rechazados/Eliminados"})
		
		
def aprobado(request,Post_Id,value):
	username = request.user
	if not (username.userprofile.moderador or username.is_staff):
		return PermissionDenied
	post = Post.objects.get(pk=Post_Id)
	if (int(value)==1):
		post.aprobado = True
		if post.reply_to:
			thread = Thread.objects.get(op=post.reply_to)
			thread.respuestas += 1
			thread.save()
	else:
		post.aprobado = False
		if post.reply_to:
			thread = Thread.objects.get(op=post.reply_to)
			thread.respuestas -= 1
			thread.save()
	post.save()
	return redirect(reverse('foro:aprobar'))
	
def usuarios(request):
	username = request.user
	if not (username.userprofile.moderador or username.is_staff):
		raise PermissionDenied
	admins = []
	staff = User.objects.filter(is_staff=True,is_active=True)
	moderadores = User.objects.filter(is_staff=False,is_active=True,userprofile__moderador=True)
	#moderadores = UserProfile.objects.filter(moderador=True,user__is_staff=False,user__is_active=True)
	usuarios =	User.objects.filter(is_staff=False,userprofile__moderador=False,is_active=True)
	usuariosN = User.objects.filter(is_active=False)
	return render(request, "Foro/usuarios.html", {'usuario':username, 'staff':staff,'moderadores':moderadores,'usuarios':usuarios,'usuarios_No_Actvo':usuariosN})
	
def banHammer(request,user_id):
	username = request.user
	if not (username.userprofile.moderador or username.is_staff):
		return PermissionDenied
	try:
		usuario = User.objects.get(id=int(user_id))
		if not (usuario.is_staff):
			if(usuario.is_active):
				usuario.is_active = False
			else:
				usuario.is_active = True
			usuario.save()
	except User.DoesNotExist:
		raise Http404("Usuario no existe")
	return redirect(reverse('foro:usuarios'))

def admin_posts(request):
	username = request.user
	categorias = Thread.objects.order_by().values_list('category',flat=True).distinct()
	return render(request, "Foro/buscar.html", {'usuario':username,'categorias':categorias})

def buscar(request):
	username = request.user
	categorias = Thread.objects.order_by().values_list('category', flat=True).distinct()
	all_posts = dict()
	try:
		usuario = User.objects.get(username=request.POST['usuario'])
	except User.DoesNotExist:
		raise Http404("Usuario no existe")
	categoria = request.POST['categoria']
	posts = Post.objects.filter(owner=usuario).order_by("id")
	for post in posts:
		if post.reply_to:
			all_posts[post] = Thread.objects.get(op=post.reply_to,category=categoria)
		else:
			all_posts[post] = Thread.objects.get(op=post,category=categoria)
	return render(request, "Foro/buscar.html", {'usuario': username, 'categorias': categorias, 'all_posts':all_posts})


def repo(request):
	username = request.user
	return render(request, "Foro/repositorio.html",{'usuario':username})

'''
class PostList(APIView):

	def get(self, request):
		posts = Post.objects.all()
		serializer = PostSerializer(posts,many=True)
		return Response(serializer.data)
'''