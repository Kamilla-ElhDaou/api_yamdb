from django.contrib import admin

from .models import Comment, Review


admin.site.empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели Comment."""

    list_display = ('review', 'author', 'text', 'pub_date')
    search_fields = ('review', 'author__username',)
    list_filter = ('review', 'author',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели Review."""

    list_display = ('title', 'author', 'text', 'score', 'pub_date',)
    search_fields = ('title', 'author__username', 'text', 'score',)
    list_filter = ('title', 'author', 'score',)
