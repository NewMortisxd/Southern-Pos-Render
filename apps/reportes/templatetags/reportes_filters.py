from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def divide_by(value, arg):
    """Divides the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return value

@register.filter
def calculate_iva(value):
    """Calculates the IVA amount (15%) from the total price"""
    try:
        total = float(value)
        subtotal = total / 1.15
        return total - subtotal
    except (ValueError, TypeError):
        return 0