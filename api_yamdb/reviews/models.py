from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify

from constants import CHAR_LIMIT, MAX_NAME_LENGTH, MAX_SCORE, MIN_SCORE


User = get_user_model()


class CategoryGenreBaseModel(models.Model):
    """Базовая модель для категории и жанров."""

    name = models.CharField(max_length=MAX_NAME_LENGTH,
                            verbose_name='Название',)
    slug = models.SlugField(unique=True,
                            verbose_name='Идентификатор',)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:CHAR_LIMIT]
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(CategoryGenreBaseModel):
    """
    Модель для категории произведений.

    Атрибуты:
        name (CharField): Название категории.
        slug (SlugField): Уникальный идентификатор для URL.
    """

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Genre(CategoryGenreBaseModel):
    """
    Модель для жанра произведений.

    Атрибуты:
        name (CharField): Название жанра.
        slug (SlugField): Уникальный идентификатор для URL.
    """

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """
    Модель для произведения.

    Атрибуты:
        name (CharField): Название произведения.
        year (PositiveIntegerField): Год выпуска.
        description (TextField): Описание.
        genre (ManyToManyField): Жанр.
        category (ForeignKey): Категория.
    """

    name = models.CharField(max_length=MAX_NAME_LENGTH,
                            verbose_name='Название',)
    year = models.PositiveSmallIntegerField(
        verbose_name='Год выпуска',
        validators=[MaxValueValidator(datetime.now().year)],
    )
    description = models.TextField(verbose_name='Описание', blank=True,)
    genre = models.ManyToManyField(Genre,
                                   verbose_name='Жанр',
                                   blank=True,)
    category = models.ForeignKey(Category,
                                 verbose_name='Категория',
                                 null=True,
                                 blank=True,
                                 on_delete=models.SET_NULL,)

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'
        default_related_name = 'titles'
        ordering = ['name']
        indexes = [
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.name


class ReviewCommentBaseModel(models.Model):
    """
    Базовая модель для отзывов и комментариев.

    Атрибуты:
        author (ForeignKey): Автор.
        text (TextField): Текст.
        pub_date (DateTimeField): Дата добавления.
    """

    author = models.ForeignKey(User,
                               verbose_name='Автор',
                               on_delete=models.CASCADE,)
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(verbose_name='Дата добавления',
                                    auto_now_add=True,
                                    db_index=True,)

    class Meta:
        abstract = True
        ordering = ['-pub_date']


class Review(ReviewCommentBaseModel):
    """
    Модель для отзыва на произведение.

    Атрибуты:
        title (ForeignKey): Произведение.
        score (PositiveIntegerField): Оценка.

        Поля унаследованы от ReviewCommentBaseModel:
            author, text, pub_date
    """

    title = models.ForeignKey(Title,
                              verbose_name='Произведение',
                              on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(MIN_SCORE), MaxValueValidator(MAX_SCORE)
        ],
    )

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            )
        ]
        default_related_name = 'reviews'
        indexes = [
            models.Index(fields=['title', 'author']),
        ]

    def __str__(self):
        return f'Отзыв {self.author} на {self.title}'


class Comment(ReviewCommentBaseModel):
    """
    Модель для комментария к отзыву.

    Атрибуты:
        review (ForeignKey): Отзыв.

        Поля унаследованы от ReviewCommentBaseModel:
            author, text, pub_date
    """

    review = models.ForeignKey(Review,
                               verbose_name='Отзыв',
                               on_delete=models.CASCADE,)

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
        indexes = [
            models.Index(fields=['review', 'author']),
        ]

    def __str__(self):
        return f'Комментарий {self.author} к отзыву {self.review.id}'
