from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def divide_by_iva(value):
    """
    Divide a value by 1.15 (15% IVA rate) to get the pre-tax value
    """
    try:
        # Using 15% IVA rate
        iva_rate = Decimal('1.15')
        return Decimal(value) / iva_rate
    except (ValueError, TypeError, ZeroDivisionError):
        return value

@register.filter
def without_iva(value):
    """Remove 15% IVA from a value"""
    if value is None or value == '':
        return 0
    return Decimal(value) / (Decimal('1') + IVA_RATE)

@register.filter
def calculate_iva(value):
    """Calculate 15% IVA from a pre-tax value"""
    if value is None or value == '':
        return 0
    return Decimal(value) * IVA_RATE

@register.filter
def calculate_total(value):
    """Calculate total from pre-tax value (adding 15% IVA)"""
    if value is None or value == '':
        return 0
    subtotal = Decimal(value)
    iva = subtotal * IVA_RATE
    return subtotal + iva


@register.filter
def subtract_pretax(value):
    """
    Calculate the IVA amount by subtracting the pre-tax value from the total
    """
    try:
        total = Decimal(value)
        pretax = total / Decimal('1.15')
        return total - pretax
    except (ValueError, TypeError, ZeroDivisionError):
        return value
