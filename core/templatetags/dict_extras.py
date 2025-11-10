from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """
    Template filter to get dictionary value by key.
    Usage: {{ dict|lookup:key }}
    """
    if hasattr(dictionary, 'get'):
        return dictionary.get(key, '')
    return ''

@register.filter
def get_item(dictionary, key):
    """
    Alternative template filter for dictionary access.
    """
    return dictionary.get(key) 