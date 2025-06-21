from django.contrib import admin

from reviews.models import Category, Comment, Genre, Review, Title


admin.site.empty_value_display = '-пусто-'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели категорий."""

    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели жанров."""

    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели произведений."""

    list_display = ('name', 'year', 'description',
                    'category', 'display_genres')
    search_fields = ('name', 'year', 'category__name')
    list_filter = ('year', 'category', 'genre')
    filter_horizontal = ('genre',)
    list_select_related = ('category',)
    list_editable = ('category',)

    @admin.display(description='Жанры')
    def display_genres(self, obj):
        """Отображает жанры через запятую."""
        return ", ".join([genre.name for genre in obj.genre.all()])

    def get_queryset(self, request):
        """Оптимизация запроса с предзагрузкой жанров."""
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('genre')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели комментариев."""

    list_display = ('review', 'author', 'text', 'pub_date')
    search_fields = ('review', 'author__username',)
    list_filter = ('review', 'author',)
    list_select_related = ('title', 'author')
    date_hierarchy = 'pub_date'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели отзывов."""

    list_display = ('title', 'author', 'text', 'score', 'pub_date',)
    search_fields = ('title', 'author__username', 'text', 'score',)
    list_filter = ('title', 'author', 'score',)
    list_select_related = ('title', 'author')
    date_hierarchy = 'pub_date'
