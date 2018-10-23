from django import template

register = template.Library()


@register.filter(name='lookup')
def lookup(value, arg):
    return value[arg]
#
#
# @register.filter(name='lookupIPv6')
# def lookupIPv6(value, arg):
#     return value[arg]
