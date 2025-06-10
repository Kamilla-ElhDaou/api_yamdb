from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Comment, Review


User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)
        read_only_fields = ('id', 'pub_date',)


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели отзыва."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        read_only_fields = ('id', 'pub_date',)

    def validate_score(self, data):
        if not 1 <= data <= 10:
            raise serializers.ValidationError('Оценка должна быть от 1 до 10')
        return data
