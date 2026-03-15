from django import template

register = template.Library()


@register.filter
def get_field(obj, field_name):
    """Get a model field value dynamically by name."""
    return getattr(obj, field_name, None) or ""
