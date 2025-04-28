from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

from content.views import PostViewSet, CommentViewSet

app_name = "content"

router = DefaultRouter()
router.register("posts", PostViewSet, basename="post")

posts_router = NestedSimpleRouter(router, "posts", lookup="post")
posts_router.register("comments", CommentViewSet, basename="post-comment")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(posts_router.urls)),
]
