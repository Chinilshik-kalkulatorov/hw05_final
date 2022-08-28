from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Страничка автора проекта"""
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Страничка о примененных технологиях"""
    template_name = 'about/tech.html'
