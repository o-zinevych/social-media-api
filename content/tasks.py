from celery import shared_task
from django.db.models import Q
from django.utils import timezone

from content.models import Post


@shared_task
def publish_scheduled_posts() -> None:
    Post.objects.filter(
        Q(is_published=False) & Q(scheduled_at__lte=timezone.now())
    ).update(is_published=True)
