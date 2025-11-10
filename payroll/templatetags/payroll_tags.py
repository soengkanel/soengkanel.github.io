"""
Template tags for payroll currency formatting
"""
from django import template
from django.utils.safestring import mark_safe
from decimal import Decimal

register = template.Library()


@register.simple_tag
def format_currency(amount):
    """
    Format amount according to payroll settings
    Usage: {% format_currency salary_slip.net_pay %}
    """
    from payroll.models import PayrollSettings

    settings = PayrollSettings.get_settings()
    return settings.format_currency(amount)


@register.simple_tag
def currency_code():
    """
    Get the current currency code
    Usage: {% currency_code %}
    """
    from payroll.models import PayrollSettings

    settings = PayrollSettings.get_settings()
    return settings.base_currency


@register.simple_tag
def currency_symbol():
    """
    Get the current currency symbol
    Usage: {% currency_symbol %}
    """
    from payroll.models import PayrollSettings

    settings = PayrollSettings.get_settings()
    return settings.currency_symbol


@register.filter
def format_amount(amount, decimal_places=None):
    """
    Format amount with thousand separators and decimal places
    Usage: {{ amount|format_amount }} or {{ amount|format_amount:0 }}
    """
    from payroll.models import PayrollSettings

    if amount is None:
        amount = 0

    # Convert to Decimal if needed
    if not isinstance(amount, Decimal):
        try:
            amount = Decimal(str(amount))
        except:
            amount = Decimal('0')

    settings = PayrollSettings.get_settings()

    # Use provided decimal places or settings default
    if decimal_places is None:
        decimal_places = settings.decimal_places
    else:
        decimal_places = int(decimal_places)

    # Format with decimal places
    if decimal_places == 0:
        formatted = f"{amount:,.0f}" if settings.use_thousand_separator else f"{amount:.0f}"
    else:
        formatted = f"{amount:,.2f}" if settings.use_thousand_separator else f"{amount:.2f}"

    return formatted


@register.simple_tag
def currency_display(amount, show_code=False):
    """
    Display amount with currency symbol and optional code
    Usage: {% currency_display salary_slip.net_pay %} or {% currency_display salary_slip.net_pay True %}
    """
    from payroll.models import PayrollSettings

    settings = PayrollSettings.get_settings()
    formatted = settings.format_currency(amount)

    if show_code:
        formatted = f"{formatted} {settings.base_currency}"

    return formatted


@register.simple_tag(takes_context=True)
def get_payroll_settings(context):
    """
    Add payroll settings to template context
    Usage: {% get_payroll_settings %}
    Then access: {{ payroll_settings.base_currency }}
    """
    from payroll.models import PayrollSettings

    context['payroll_settings'] = PayrollSettings.get_settings()
    return ''


@register.inclusion_tag('payroll/partials/currency_info.html')
def show_currency_info():
    """
    Display currency information widget
    Usage: {% show_currency_info %}
    """
    from payroll.models import PayrollSettings

    settings = PayrollSettings.get_settings()
    return {
        'currency_code': settings.base_currency,
        'currency_symbol': settings.currency_symbol,
        'currency_name': settings.get_currency_display_name(),
    }
