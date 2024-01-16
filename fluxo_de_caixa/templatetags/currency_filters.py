from django import template
import locale

register = template.Library()

@register.filter(name='currency_br')
def currency_br(value):
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        return locale.currency(value, grouping=True)
    except ValueError:
        return value