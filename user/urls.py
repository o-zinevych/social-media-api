from django.urls import path, include
from rest_framework import routers

from user.views import (
    RegisterUserView,
    LoginUserView,
    LogoutUserView,
    ManageUserView,
)

app_name = "user"

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("login/", LoginUserView.as_view(), name="login"),
    path("logout/", LogoutUserView.as_view(), name="logout"),
    path("me/", ManageUserView.as_view(), name="manage"),
]
