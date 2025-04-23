from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user.views import (
    RegisterUserView,
    LoginUserView,
    LogoutUserView,
    ManageUserView,
    UserImageUploadView,
    UserViewSet,
)

app_name = "user"

router = DefaultRouter()
router.register("", UserViewSet, basename="user")

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("login/", LoginUserView.as_view(), name="login"),
    path("logout/", LogoutUserView.as_view(), name="logout"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path("me/upload-image/", UserImageUploadView.as_view(), name="upload-image"),
    path("", include(router.urls)),
]
