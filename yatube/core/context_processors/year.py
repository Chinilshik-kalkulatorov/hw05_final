from django.utils import timezone


def year(request):
    """Добавляет в контекст переменную с текущим годом."""
    return {'year': timezone.now().year}
