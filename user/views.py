from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, status, viewsets, mixins
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.compat import coreapi, coreschema
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.schemas import coreapi as coreapi_schema, ManualSchema
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from user.serializers import (
    UserSerializer,
    UserUpdateSerializer,
    UserRetrieveSerializer,
    UserImageSerializer,
    UserFollowingSerializer,
    UserTokenSerializer,
)


class RegisterUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class LoginUserView(ObtainAuthToken):
    serializer_class = UserTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    if coreapi_schema.is_enabled():
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="email",
                    required=True,
                    location="form",
                    schema=coreschema.String(
                        title="Email",
                        description="Valid email for authentication",
                    ),
                ),
                coreapi.Field(
                    name="password",
                    required=True,
                    location="form",
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    ),
                ),
            ],
            encoding="application/json",
        )


class LogoutUserView(APIView):
    """Allows registered users to invalidate their token"""

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response(
                {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
            )
        except Token.DoesNotExist:
            return Response(
                {"detail": "Token not found."}, status=status.HTTP_404_NOT_FOUND
            )


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == "PUT" or self.request.method == "PATCH":
            return UserUpdateSerializer
        return UserRetrieveSerializer


class UserImageUploadView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = UserImageSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    def get_queryset(self):
        queryset = get_user_model().objects.prefetch_related("followers", "following")

        username = self.request.query_params.get("username")
        if username:
            queryset = queryset.filter(username__icontains=username)

        first_name = self.request.query_params.get("first_name")
        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)

        last_name = self.request.query_params.get("last_name")
        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserRetrieveSerializer
        if self.action in ("follow", "unfollow"):
            return UserFollowingSerializer
        return UserSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="username",
                description="Filter user list by case-insensitive username.",
            ),
            OpenApiParameter(
                name="first_name",
                description="Filter user list by case-insensitive first name.",
            ),
            OpenApiParameter(
                name="last_name",
                description="Filter user list by case-insensitive last name.",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(
        methods=["POST"],
        detail=True,
        url_path="follow",
        permission_classes=[IsAuthenticated],
    )
    def follow(self, request, pk=None):
        current_user = request.user
        user_to_follow = self.get_object()

        if current_user.id == user_to_follow.id:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if current_user in user_to_follow.followers.all():
            return Response(
                {"detail": "You are already following this user."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user_to_follow.followers.add(current_user)
        current_user.following.add(user_to_follow)
        return Response(
            {"detail": "Successfully followed this user."}, status=status.HTTP_200_OK
        )

    @action(
        methods=["POST"],
        detail=True,
        url_path="unfollow",
        permission_classes=[IsAuthenticated],
    )
    def unfollow(self, request, pk=None):
        current_user = request.user
        user_to_unfollow = self.get_object()

        if current_user.id == user_to_unfollow.id:
            return Response(
                {"detail": "You cannot unfollow yourself."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if current_user not in user_to_unfollow.followers.all():
            return Response(
                {"detail": "You aren't following this user."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user_to_unfollow.followers.remove(current_user)
        current_user.following.remove(user_to_unfollow)
        return Response(
            {"detail": "Successfully unfollowed this user."}, status=status.HTTP_200_OK
        )
