from rest_framework import generics, mixins
from .serializers import PostSerializer, ThreadSerializer
from ..models import Post, Thread


class PostAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    lookup_field = 'pk'
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PostUserAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    lookup_field = 'pk'
    serializer_class= PostSerializer

    def get_queryset(self):
        uid = self.kwargs.get("pk")
        return Post.objects.filter(owner_id=uid)


class PostRudView(generics.RetrieveUpdateAPIView):
    lookup_field = 'pk'
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.all()



class ThreadAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    lookup_field = 'categoria'
    serializer_class = ThreadSerializer

    def get_queryset(self):
        cat = self.kwargs.get('categoria')
        return Thread.objects.filter(category=cat)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ThreadRudView(generics.RetrieveUpdateAPIView):
    lookup_field = 'pk'
    serializer_class = ThreadSerializer

    def get_queryset(self):
        return Thread.objects.all()