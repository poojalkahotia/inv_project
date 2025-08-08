from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
    try:
        return value.as_widget(attrs={'class': css_class})
    except AttributeError:
        return value  # fallback if it's a string
