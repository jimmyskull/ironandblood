from django import template

from game.config import Config

register = template.Library()

@register.simple_tag
def get_verbose_field_name(instance, field_name):
    """
    Returns verbose_name for a field.
    """
    return instance._meta.get_field(field_name).verbose_name.title()

@register.simple_tag
def get_field_value(instance, field_name):
    """
    Returns verbose_name for a field.
    """
    return getattr(instance, field_name)

@register.simple_tag
def current_game_date():
  return Config.current_game_date()

@register.simple_tag
def to_game_date(date):
  return Config.to_game_date(date)
