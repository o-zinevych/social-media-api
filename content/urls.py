from django.urls import path, include
from rest_framework.routers import DefaultRouter

from content.views import PostViewSet

app_name = "content"

router = DefaultRouter()
router.register("posts", PostViewSet, basename="post")

urlpatterns = [path("", include(router.urls))]
