import csv
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from reviews.models import Category, Comment, Genre, Review, Title


User = get_user_model()


class Command(BaseCommand):
    """Загрузка файлов из CSV файлов."""

    DATA_PATH = 'static/data/'
    DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
    CSV_ENCODING = 'utf-8'

    help = 'Load data from CSV files into database'

    def handle(self, *args, **options):
        """Основной метод обработки команды."""
        loaders = {
            'users.csv': (User, self.load_data),
            'category.csv': (Category, self.load_data),
            'genre.csv': (Genre, self.load_data),
            'titles.csv': (None, self.load_titles),
            'genre_title.csv': (None, self.load_genre_title),
            'review.csv': (Review, self.load_reviews_comments),
            'comments.csv': (Comment, self.load_reviews_comments),
        }

        for filename, (model, func) in loaders.items():
            if model:
                func(filename, model)
            else:
                func(filename)

        self.stdout.write(self.style.SUCCESS('Данные успешно загружены!'))

    def load_data(self, filename, model):
        """Общая функция загрузки моделей категорий и жанров."""
        with open(
            f'{self.DATA_PATH}{filename}', encoding=self.CSV_ENCODING
        ) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data = {**row}
                try:
                    model.objects.get_or_create(**data)
                except IntegrityError:
                    self.stdout.write(self.style.WARNING(
                        f'Объект уже существует: {model.__name__} {data}'
                    ))

    def load_titles(self, filename):
        """Загрузка произведений."""
        with open(
            f'{self.DATA_PATH}{filename}', encoding=self.CSV_ENCODING
        ) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    category = Category.objects.get(id=row.pop('category'))
                    Title.objects.create(
                        category=category,
                        **row,
                    )
                except Category.DoesNotExist:
                    self.stdout.write(self.style.ERROR(
                        f'Категория с id={row["category"]} не найдена!'
                    ))

    def load_genre_title(self, filename):
        """Загрузка жанра к произведению (связь ManyToMany)."""
        with open(
            f'{self.DATA_PATH}{filename}', encoding=self.CSV_ENCODING
        ) as csvfile:
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

    def load_reviews_comments(self, filename, model):
        """Общая функция загрузки моделей комментариев и отзывов."""
        with open(
            f'{self.DATA_PATH}{filename}', encoding=self.CSV_ENCODING
        ) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    data_kwargs = {}

                    if model == Review:
                        data_kwargs['title'] = Title.objects.get(
                            id=row.pop('title_id')
                        )
                    else:
                        data_kwargs['review'] = Review.objects.get(
                            id=row.pop('review_id')
                        )

                    data_kwargs['author'] = User.objects.get(
                        id=row.pop('author')
                    )

                    row['pub_date'] = datetime.strptime(
                        row['pub_date'], self.DATE_FORMAT
                    )

                    model.objects.create(**data_kwargs, **row)

                except (
                    (Title if model == Review else Review).DoesNotExist
                ) as error:
                    self.stdout.write(self.style.ERROR(
                        f'Ошибка в объекте {model.__name__} '
                        f'{row["id"]}: {str(error)}'
                    ))
                except (User.DoesNotExist) as error:
                    self.stdout.write(self.style.ERROR(
                        f'Пользователь {row["author"]} не найден: {str(error)}'
                    ))
