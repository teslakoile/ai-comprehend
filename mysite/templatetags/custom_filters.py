from django import template

register = template.Library()

@register.filter
def get_item(value, arg):
    index_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    index = index_map.get(arg.upper(), -1)
    if index >= 0 and index < len(value):
        return value[index]
    return None
