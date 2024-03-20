from django import template
from itertools import groupby as it_groupby

register = template.Library()

@register.filter
def groupby(data, attr):
    # Primeiro, filtramos os dados para remover qualquer item do grupo que queremos ignorar
    if hasattr(data, 'exclude'):
        # Se 'data' é um QuerySet do Django, usamos o método 'exclude'
        data = data.exclude(group='Transferência entre Contas')
    else:
        # Se 'data' é uma lista, usamos compreensão de lista para filtrar
        data = [item for item in data if getattr(item, 'group', '') != 'Transferência entre Contas']
    
    sorted_data = data if hasattr(data, 'order_by') else sorted(data, key=lambda x: getattr(x, attr))
    result = [(key, list(group)) for key, group in it_groupby(sorted_data, key=lambda x: getattr(x, attr))]
    return result
