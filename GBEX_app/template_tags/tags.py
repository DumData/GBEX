from django import template
from django.urls import reverse
from django.apps import apps
import random

register = template.Library()


@register.filter
def to_class_name(value):
    return value.__class__.__name__


@register.inclusion_tag('GBEX_app/links.html')
def links(selected_model, return_url="", return_text=""):
    menus = {}
    selected_menu = ""
    for model in apps.get_app_config('GBEX_app').get_models():
        if getattr(model, "model_kind", False) == "GBEX_Page":
            model_menu = model.menu_label
            if model.__name__ == selected_model:
                selected_menu = model_menu
            if model_menu in menus:
                menus[model_menu][model.__name__] = reverse(f"list_{model.__name__}")
            else:
                menus[model_menu] = {model.__name__: reverse(f"list_{model.__name__}")}
    return {
        "menus": menus,
        "selected_model": selected_model,
        "selected_menu": selected_menu,
        "return_url": return_url,
        "return_text": return_text
    }


@register.simple_tag
def random_int(a, b=None):
    if b is None:
        a, b = 0, a
    return random.randint(a, b)
