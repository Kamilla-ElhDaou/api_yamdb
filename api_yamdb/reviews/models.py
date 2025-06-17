from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify

from reviews.constants import CHAR_LIMIT


User = get_user_model()


class Category(models.Model):
    """
    Модель для категории произведений.

    Атрибуты:
        name (CharField): Название категории.
        slug (SlugField): Уникальный идентификатор для URL.
    """

    name = models.CharField(max_length=256, verbose_name='Название')
    slug = models.SlugField(max_length=50,
                            unique=True,
                            verbose_name='Идентификатор',)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:CHAR_LIMIT]
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Genre(models.Model):
    """
    Модель для жанра произведений.

    Атрибуты:
        name (CharField): Название жанра.
        slug (SlugField): Уникальный идентификатор для URL.
    """

    name = models.CharField(max_length=256, verbose_name='Название')
    slug = models.SlugField(max_length=50,
                            unique=True,
                            verbose_name='Идентификатор',)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:CHAR_LIMIT]
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']

    def __str__(self):
        return self.name


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

    name = models.CharField(max_length=256, verbose_name='Название',)
    year = models.PositiveIntegerField(verbose_name='Год выпуска',)
    description = models.TextField(verbose_name='Описание',)
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

    def __str__(self):
        return self.name


class Review(models.Model):
    """
    Модель для отзыва на произведение.

    Атрибуты:
        title (ForeignKey): Произведение.
        author (ForeignKey): Автор отзыва.
        text (TextField): Текст отзыва.
        score (PositiveIntegerField): Оценка.
        pub_date (DateTimeField): Дата добавления.
    """

    title = models.ForeignKey(Title,
                              verbose_name='Произведение',
                              on_delete=models.CASCADE)
    author = models.ForeignKey(User,
                               verbose_name='Автор отзыва',
                               on_delete=models.CASCADE,)
    text = models.TextField(verbose_name='Текст отзыва')
    score = models.PositiveIntegerField(verbose_name='Оценка',
                                        validators=[MinValueValidator(1),
                                                    MaxValueValidator(10)])
    pub_date = models.DateTimeField(verbose_name='Дата добавления',
                                    auto_now_add=True,
                                    db_index=True,)

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            )
        ]
        ordering = ['-pub_date']
        default_related_name = 'reviews'

    def __str__(self):
        return f'Отзыв {self.author} на {self.title}'


class Comment(models.Model):
    """
    Модель для комментария к отзыву.

    Атрибуты:
        review (ForeignKey): Отзыв.
        author (ForeignKey): Автор комментария.
        text (TextField): Текст комментария.
        pub_date (DateTimeField): Дата добавления.
    """

    review = models.ForeignKey(Review,
                               verbose_name='Отзыв',
                               on_delete=models.CASCADE)
    author = models.ForeignKey(User,
                               verbose_name='Автор комментария',
                               on_delete=models.CASCADE,)
    text = models.TextField(verbose_name='Текст комментария')
    pub_date = models.DateTimeField(verbose_name='Дата добавления',
                                    auto_now_add=True,
                                    db_index=True,)

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-pub_date']
        default_related_name = 'comments'

    def __str__(self):
        return f'Комментарий {self.author} к отзыву {self.review.id}'
