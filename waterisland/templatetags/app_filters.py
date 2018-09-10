from django import template

register = template.Library()


@register.filter(name='format_amount')
def format_amount(value):
    value = float(value)
    return "{0:,.2f}".format(value)
