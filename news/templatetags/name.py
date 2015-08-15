from django import template

import re

register = template.Library()


@register.filter("name")
def name(long_name, long_or_short):
    if long_or_short == 'short':
        name = str(long_name.split("_")[0])
    else:
        name = str(long_name.replace("_", " "))
    name = "".join(
        [letter for letter in name if re.match(r'^[a-zA-Z ]+$', name)])
    return name.title()
