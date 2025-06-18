import csv
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from reviews.models import Category, Comment, Genre, Review, Title


User = get_user_model()


class Command(BaseCommand):
    """Загрузка файлов из CSV файлов."""

    help = 'Load data from CSV files into database'

    def handle(self, *args, **options):
        self.load_users()
        self.load_categories()
        self.load_genres()
        self.load_titles()
        self.load_genre_title()
        self.load_reviews()
        self.load_comments()
        self.stdout.write(self.style.SUCCESS('Данные успешно загружены!'))

    def load_users(self):
        """Загрузка пользователей."""
        with open('static/data/users.csv', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                user_data = {
                    'id': row['id'],
                    'username': row['username'],
                    'email': row['email'],
                    'role': row['role'],
                    'bio': row.get('bio', ''),
                    'first_name': row.get('first_name', ''),
                    'last_name': row.get('last_name', ''),
                }
                try:
                    User.objects.create(**user_data)
                except IntegrityError:
                    self.stdout.write(self.style.WARNING(
                        f'Пользователь {row["username"]} уже существует'
                    ))

    def load_categories(self):
        """Загрузка категорий."""
        with open('static/data/category.csv', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                сategory_data = {
                    'id': row['id'],
                    'name': row['name'],
                    'slug': row['slug'],
                }
                Category.objects.get_or_create(**сategory_data)

    def load_genres(self):
        """Загрузка жанров."""
        with open('static/data/genre.csv', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                genre_data = {
                    'id': row['id'],
                    'name': row['name'],
                    'slug': row['slug'],
                }
                Genre.objects.get_or_create(**genre_data)

    def load_titles(self):
        """Загрузка произведений."""
        with open('static/data/titles.csv', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                category = Category.objects.get(id=row['category'])
                Title.objects.create(
                    id=row['id'],
                    name=row['name'],
                    year=row['year'],
                    category=category,
                )

    def load_genre_title(self):
        """Загрузка жанра к произведению (связь ManyToMany)."""
        with open('static/data/genre_title.csv', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    title = Title.objects.get(id=row['title_id'])
                    genre = Genre.objects.get(id=row['genre_id'])

                    title.genre.add(genre)

                except Title.DoesNotExist:
                    self.stdout.write(self.style.ERROR(
                        f'Произведение с id={row["title_id"]} не найдено!'
                    ))

                except Genre.DoesNotExist:
                    self.stdout.write(self.style.ERROR(
                        f'Жанр с id={row["genre_id"]} не найден!'
                    ))

                except IntegrityError:
                    self.stdout.write(self.style.WARNING(
                        f'Связь title_id={row["title_id"]} '
                        f'и genre_id={row["genre_id"]} уже существует'
                    ))

    def load_reviews(self):
        """Загрузка отзывов."""
        with open('static/data/review.csv', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    title = Title.objects.get(id=row['title_id'])
                    author = User.objects.get(id=row['author'])
                    Review.objects.create(
                        id=row['id'],
                        title=title,
                        text=row['text'],
                        author=author,
                        score=row['score'],
                        pub_date=datetime.strptime(
                            row['pub_date'], '%Y-%m-%dT%H:%M:%S.%fZ'
                        ),
                    )
                except (Title.DoesNotExist, User.DoesNotExist) as error:
                    self.stdout.write(self.style.ERROR(
                        f'Ошибка в отзыве {row["id"]}: {str(error)}'
                    ))

    def load_comments(self):
        """Загрузка комментариев."""
        with open('static/data/comments.csv', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    review = Review.objects.get(id=row['review_id'])
                    author = User.objects.get(id=row['author'])
                    Comment.objects.create(
                        id=row['id'],
                        review=review,
                        text=row['text'],
                        author=author,
                        pub_date=datetime.strptime(
                            row['pub_date'], '%Y-%m-%dT%H:%M:%S.%fZ'
                        ),
                    )
                except (Review.DoesNotExist, User.DoesNotExist) as error:
                    self.stdout.write(self.style.ERROR(
                        f'Ошибка в комментарии {row["id"]}: {str(error)}'
                    ))
