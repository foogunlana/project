from django import template

register = template.Library()


@register.filter('replace')
def replace(string, ois):
    try:
        ois = ois.split(',')
        o, i = ois[0], ois[1]
        string = string.replace(o, i)
    except Exception:
        pass
    return string
