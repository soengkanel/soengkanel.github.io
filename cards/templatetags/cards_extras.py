from django import template

register = template.Library()


@register.filter
def slice_cards(cards_list, cards_per_page):
    """
    Slice the cards list into pages with specified number of cards per page.
    Returns a list of lists (pages).
    """
    cards_per_page = int(cards_per_page)
    if cards_per_page <= 0:
        return [cards_list]
    
    pages = []
    for i in range(0, len(cards_list), cards_per_page):
        pages.append(cards_list[i:i + cards_per_page])
    
    return pages


@register.filter
def slice_range(total_count, start_from):
    """
    Create a range starting from start_from to total_count.
    Used for filling empty card slots.
    """
    total_count = int(total_count)
    start_from = int(start_from)
    
    if start_from >= total_count:
        return []
    
    return range(start_from, total_count)


@register.filter
def divide(value, divisor):
    """
    Divide value by divisor and return the result.
    """
    try:
        return int(value) / int(divisor)
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter
def ceil_divide(value, divisor):
    """
    Divide value by divisor and return the ceiling of the result.
    """
    import math
    try:
        return math.ceil(int(value) / int(divisor))
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter
def batch_size(cards_list, layout):
    """
    Return the number of cards per page based on layout.
    """
    layout_sizes = {
        'single': 1,
        'grid_2x2': 4,
        'grid_3x3': 9,
        'grid_4x4': 16,
    }
    return layout_sizes.get(layout, 4)


@register.filter
def mul(value, multiplier):
    """
    Multiply value by multiplier and return the result.
    """
    try:
        if value is None or multiplier is None:
            return 0
        return float(value) * float(multiplier)
    except (ValueError, TypeError):
        return 0


@register.filter
def div(value, divisor):
    """
    Divide value by divisor and return the result.
    Enhanced version with better error handling.
    """
    try:
        if value is None or divisor is None:
            return 0
        if float(divisor) == 0:
            return 0
        return float(value) / float(divisor)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0 