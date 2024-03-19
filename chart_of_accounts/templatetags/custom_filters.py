from django import template
from itertools import groupby as it_groupby

register = template.Library()

@register.filter
def groupby(data, attr):
    # If data is a QuerySet, we don't need to sort it as it should already be ordered
    sorted_data = data if hasattr(data, 'order_by') else sorted(data, key=lambda x: getattr(x, attr))
    
    # Group data and create a list of tuples
    result = [(key, list(group)) for key, group in it_groupby(sorted_data, key=lambda x: getattr(x, attr))]
    return result