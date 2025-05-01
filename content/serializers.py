from rest_framework import serializers

from content.models import Post, Comment


class PostSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    likes = serializers.IntegerField(read_only=True, source="likes_count")
    liked_by_me = serializers.SerializerMethodField(read_only=True)
    scheduled_at = serializers.DateTimeField(
        write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "text",
            "image",
            "scheduled_at",
            "user",
            "posted_at",
            "likes",
            "liked_by_me",
        )
        read_only_fields = (
            "id",
            "user",
            "posted_at",
            "likes",
            "liked_by_me",
        )

    def get_liked_by_me(self, obj):
        user = self.context["request"].user
        return obj.likes.filter(id=user.id).exists()


class PostRetrieveSerializer(PostSerializer):
    comments = serializers.StringRelatedField(many=True, read_only=True)

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ("comments",)


class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ()


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "comment", "user", "posted_at")
        read_only_fields = ("id", "user", "posted_at")
