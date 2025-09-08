from django import template
import os

register = template.Library()

@register.filter
def is_image(filename):
    """
    Retorna True se a extensão do nome for de imagem conhecida.
    Use com: {{ an.arquivo.name|is_image }}
    """
    ext = os.path.splitext(str(filename).lower())[1]
    return ext in {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg'}
