# api_YaMDb
YaMDb - это платформа для сбора отзывов пользователей на различные произведения (книги, фильмы, музыку). Проект предоставляет REST API для взаимодействия с платформой.

## Основные возможности

### Аутентификация и управление пользователями
- Регистрация новых пользователей через email с подтверждением
- JWT-аутентификация (JSON Web Tokens)
- Ролевая система:
    * Анонимные пользователи (только чтение)
    * Аутентифицированные пользователи (отзывы и комментарии)
    * Модераторы (могут модерировать контент)
    * Администраторы (полные права)
- Управление профилем через /users/me/
- Поиск пользователей по username
### Работа с произведениями
- Категории и жанры произведений
- Фильтрация произведений по:
    * Категории
    * Жанру
    * Году выпуска
    * Названию
- Рейтинг произведений на основе пользовательских оценок
- Подробная информация о каждом произведении

### Система отзывов и оценок
- Пользовательские отзывы на произведения
- Оценки от 1 до 10 для каждого отзыва
- Автоматический расчет среднего рейтинга произведения
- Ограничение: 1 отзыв на произведение от пользователя
- Комментарии к отзывам с возможностью обсуждения

### Модерация контента
- Удаление/редактирование любых отзывов и комментариев (для модераторов и админов)
- Управление категориями и жанрами (только для админов)
- Блокировка пользователей (для админов)

### Поиск и фильтрация
- Полнотекстовый поиск по:
    * Названиям произведений
    * Именам пользователей
    * Текстам отзывов и комментариев

- Сортировка по:
    * Дате добавления
    * Рейтингу
    * Количеству отзывов

## Используемые технологии

### Основной стек

- **Python 3.9+** - Язык программирования
- **Django 3.2** - Веб-фреймворк
- **Django REST Framework 3.12** - REST API
- **SQLite3** - База данных
- **SimpleJWT 4.6** - JWT-аутентификация

### Дополнительные инструменты
- **Pytest 6.2** - Тестирование

## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Kamilla-ElhDaou/api_final_yatube.git
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

## API Endpoints
[Документация](http://127.0.0.1:8000/redoc/) для API Yatube в формате Redoc.<br/>Для полного описания API смотрите документацию по эндпоинтам после запуска сервера.
### Аутентификация
POST /api/v1/auth/signup/ - Регистрация нового пользователя<br/>
```
{
  "email": "user@example.com",
  "username": "^w\\Z"
}
```
POST /api/v1/auth/token/ - Получение JWT-токена<br/>
```
{
  "username": "^w\\Z",
  "confirmation_code": "string"
}
```
### Пользователи
GET /api/v1/users/ - Список пользователей (admin only)<br/>
```
{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "username": "^w\\Z",
      "email": "user@example.com",
      "first_name": "string",
      "last_name": "string",
      "bio": "string",
      "role": "user"
    }
  ]
}
```
GET /api/v1/users/me/ - Мой профиль (authenticated users)<br/>
```
{
  "username": "^w\\Z",
  "email": "user@example.com",
  "first_name": "string",
  "last_name": "string",
  "bio": "string",
  "role": "user"
}
```
### Произведения
GET /api/v1/titles/ - Список произведений<br/>
```
{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": 0,
      "name": "string",
      "year": 0,
      "rating": 0,
      "description": "string",
      "genre": [
        {
          "name": "string",
          "slug": "^-$"
        }
      ],
      "category": {
        "name": "string",
        "slug": "^-$"
      }
    }
  ]
}
```
PATCH /api/v1/titles/{id}/ - Изменение произведения (admin only)<br/>
```
{
  "name": "string",
  "year": 0,
  "description": "string",
  "genre": [
    "string"
  ],
  "category": "string"
}
```
### Отзывы
GET /api/v1/titles/{title_id}/reviews/ - Список отзывов<br/>
```
{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": 0,
      "text": "string",
      "author": "string",
      "score": 1,
      "pub_date": "2019-08-24T14:15:22Z"
    }
  ]
}
```
POST /api/v1/titles/{title_id}/reviews/ - Добавление отзыва (authenticated users)<br/>
```
{
  "text": "string",
  "score": 1
}
```
### Комментарии
GET /api/v1/titles/{title_id}/reviews/{review_id}/comments/ - Список комментариев<br/>
```
{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": 0,
      "text": "string",
      "author": "string",
      "pub_date": "2019-08-24T14:15:22Z"
    }
  ]
}
```
PATCH /api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/ - Удаление комментария (author/moderator/admin)<br/>
```
{
  "text": "string"
}
```
### Тестирование
Для запуска тестов:
bash
```
pytest
```
### Разработчики
- Бабенкова Елизавета<br/>
- Обухов Рафаэль<br/>
- Эль Хадж Дау Камилла<br/>
