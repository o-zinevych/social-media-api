from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    inline_serializer,
)
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from content.models import Post, Comment
from content.permissions import IsOwnerOrReadOnly
from content.serializers import (
    PostSerializer,
    PostLikeSerializer,
    CommentSerializer,
    PostRetrieveSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = (IsOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = Post.objects.select_related("user")

        text = self.request.query_params.get("text")
        if text:
            queryset = queryset.filter(text__icontains=text)
        return queryset

    def get_serializer_class(self):
        if self.action == "like":
            return PostLikeSerializer
        if self.action == "retrieve":
            return PostRetrieveSerializer
        return PostSerializer

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

    @action(
        methods=["GET"],
        detail=False,
        url_path="liked-posts",
        permission_classes=[IsAuthenticated],
    )
    def liked_posts(self, request, *args, **kwargs):
        user = self.request.user
        liked_posts = self.get_queryset().filter(likes=user.id)

        page = self.paginate_queryset(liked_posts)
        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(liked_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=None,
        responses={
            200: inline_serializer(
                name="Like Response", fields={"detail": serializers.CharField()}
            ),
        },
        description="Like or unlike a retrieved post.",
        examples=[
            OpenApiExample(
                "Liked", value={"detail": "You've liked this post."}, response_only=True
            ),
            OpenApiExample(
                "Unliked",
                value={"detail": "You've removed your like."},
                response_only=True,
            ),
        ],
    )
    @action(
        methods=["POST"],
        detail=True,
        url_path="like",
        permission_classes=[IsAuthenticated],
    )
    def like(self, request, pk=None):
        post = self.get_object()
        post_likes = post.likes.all()

        if self.request.user in post_likes:
            post.likes.remove(self.request.user)
            return Response(
                {"detail": "You've removed your like."}, status=status.HTTP_200_OK
            )

        post.likes.add(self.request.user)
        return Response(
            {"detail": "You've liked this post."}, status=status.HTTP_200_OK
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def get_queryset(self):
        post_pk = self.kwargs.get("post_pk")
        return Comment.objects.filter(post_id=post_pk)

    def perform_create(self, serializer):
        post_pk = self.kwargs.get("post_pk")
        post = Post.objects.get(pk=post_pk)
        serializer.save(user=self.request.user, post=post)
