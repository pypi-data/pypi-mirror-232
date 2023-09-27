"""
Versioned static URLs to break browser caches when changing the app version
"""

# Django
from django.template.defaulttags import register
from django.templatetags.static import static

# Alliance Auth AFAT
from afat import __version__


@register.simple_tag
def afat_static(path: str) -> str:
    """
    Versioned static URL

    :param path:
    :type path:
    :return:
    :rtype:
    """

    static_url = static(path=path)
    versioned_url = static_url + "?v=" + __version__

    return versioned_url
