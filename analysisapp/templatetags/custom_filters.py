from django import template

register = template.Library()

@register.filter
def get_field_value(obj, field_name):
    fv = getattr(obj, field_name, None) 
    return fv if fv is not None else ""

@register.filter
def get_field_name(obj:str):
    obj = obj.replace("_", " ")
    if len(obj) > 0:
        obj = obj[0].upper() + obj[1:]
    return obj

@register.filter
def replace_underscore(value):
    return value.replace("_", " ") if isinstance(value, str) else value
