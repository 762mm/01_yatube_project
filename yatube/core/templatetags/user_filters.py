from django import template  # type: ignore


register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})
