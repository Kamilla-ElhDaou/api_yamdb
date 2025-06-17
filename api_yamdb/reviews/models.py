from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


User = get_user_model()


class Category(models.Model):
    """
    Модель категории произведения.
    """

    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name
    

class Genre(models.Model):
    """
    Модель жанра произведения.
    """

    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name
    

class Title(models.Model):
    """
    Модель произведения.
    """
    name = models.CharField(max_length=256)
    year = models.PositiveSmallIntegerField()
    description = models.TextField(blank=True)
    genre = models.ManyToManyField(Genre)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)
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
