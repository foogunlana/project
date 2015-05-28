from django import template

register = template.Library()


@register.filter("array_list")
def array_list(array, index):
    index = int(index)
    try:
        element = array[index]
    except Exception as e:
        element = None

    return element
