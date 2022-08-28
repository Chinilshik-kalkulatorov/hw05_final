from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    """Фильтр шаблона форм, добавляющий атрибут form class для полей"""
    return field.as_widget(attrs={'class': css})
