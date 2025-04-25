from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from content.models import Post
from content.permissions import IsOwnerOrReadOnly
from content.serializers import PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = Post.objects.select_related("user")

        text = self.request.query_params.get("text")
        if text:
            queryset = queryset.filter(text__icontains=text)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        methods=["GET"],
        detail=False,
        url_path="my-posts",
        permission_classes=[IsAuthenticated],
    )
    def my_posts(self, request, *args, **kwargs):
        my_posts = self.get_queryset().filter(user=self.request.user)
        page = self.paginate_queryset(my_posts)

        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(my_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        url_path="following",
        permission_classes=[IsAuthenticated],
    )
    def following(self, request, *args, **kwargs):
        user = self.request.user
        followed_posts = self.get_queryset().filter(user__in=user.following.all())

        page = self.paginate_queryset(followed_posts)
        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(followed_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
