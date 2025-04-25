from rest_framework import serializers

from content.models import Post


class PostSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = ("id", "text", "image", "user", "posted_at")
        read_only_fields = (
            "id",
            "user",
            "posted_at",
        )
