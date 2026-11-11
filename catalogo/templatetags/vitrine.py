from django import template

from ..views import _fileiras_da_vitrine, _miniatura

register = template.Library()


@register.inclusion_tag('catalogo/_parede.html')
def parede_de_cartazes():
    """A parede de cartazes que corre atrás do início, do login e do cadastro."""
    return {'fileiras': _fileiras_da_vitrine()}


@register.filter
def miniatura(url):
    """Capa em miniatura de 330px quando vem da Wikimedia; outro link fica igual."""
    return _miniatura(url) if url else url
