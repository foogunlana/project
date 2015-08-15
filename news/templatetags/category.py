from django import template

register = template.Library()


@register.filter("category")
def category(string):
    if string == 'stearsMacroeconomy':
        return 'Economy'
    if string == 'stearsColumn':
        return 'Opinion'
    string = string.replace('stears', '').replace('_', ' ')
    return string
