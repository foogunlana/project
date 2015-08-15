from django import template

register = template.Library()


@register.filter("pretty_category")
def pretty_category(string):
    if string == 'stearsMacroeconomy':
        return 'Economy'
    if string == 'stearsColumn':
        return 'Opinion'
    string = string.replace('stears', '').replace('_', ' ')
    return string
