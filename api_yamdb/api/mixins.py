from rest_framework import mixins, viewsets


class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    Базовый вьюсет, предоставляет следующие действия:

    - create(создание)
    - list(получение списка)
    - destroy(удаление)

    Удобен для для моделей, где не требуется обновление и детали.
    """
