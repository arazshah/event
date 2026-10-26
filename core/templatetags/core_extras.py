from django import template

from .. import jalali

register = template.Library()


@register.filter
def fa(value):
    return jalali.fa_digits(value)


@register.filter
def jdate(value):
    return jalali.format_long(value) if value else ""


@register.filter
def jshort(value):
    return jalali.format_short(value) if value else ""


@register.filter
def iso(value):
    return value.isoformat() if value else ""


@register.filter
def jdmy(value):
    return jalali.format_dmy(value) if value else ""
