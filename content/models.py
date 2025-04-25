import pathlib
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from user.models import User


def custom_image_path(instance, filename) -> pathlib.Path:
    filename = f"{instance.id}-{uuid.uuid4()}" + pathlib.Path(filename).suffix
    return pathlib.Path("post-images") / pathlib.Path(filename)


def get_sentinel_user():
    return get_user_model().objects.get_or_create(email="deleted@deleted.com")[0]


class Post(models.Model):
    text = models.CharField(
        _("text"), max_length=255, help_text=_("Type your content here.")
    )
    image = models.ImageField(_("image"), upload_to=custom_image_path, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_sentinel_user),
        related_name="posts",
    )
    posted_at = models.DateTimeField(_("posted at"), auto_now_add=True)

    class Meta:
        ordering = ("-posted_at",)

    def __str__(self):
        return self.text
