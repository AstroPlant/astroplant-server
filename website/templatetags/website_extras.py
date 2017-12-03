from django import template
from django.core.urlresolvers import resolve
from django.shortcuts import render
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def navigation_active(request, urls):
    r = resolve(request.path_info)
    name = "%s:%s" % (r.namespace, r.url_name)
    if name in urls.split():
        return "active"
    return ""

@register.simple_tag
def root_url(request):
    absolute_uri = request.build_absolute_uri()

    # Remove trailing slash
    absolute_uri = absolute_uri[0:-1]
    return absolute_uri

@register.simple_tag
def icon(icon):
    return format_html("<span class=\"fa fa-{}\" aria-hidden=\"true\"></span>",
        icon
    )
    
@register.inclusion_tag('website/fragments/gravatar.html')
def user_avatar(user, size = 100):
    return {'user': user, 'size': size}

@register.inclusion_tag('website/fragments/user.html')
def user_with_avatar(user, avatar_size = 100):
    return {'user': user, 'avatar_size': avatar_size}

@register.filter
def key_value(dict, key):
    """
    Return the value corresponding with a given key in a dictionary.
    This is different than calling dict.key in a Django template, as
    that actually looks up dict["key"] (i.e. the string "key", an
    not the object associated with variable key).

    Usage in template: {{ dict|keyvalue:key }}

    :param dict: The dictionary to perform the lookup in.
    :param key: The key to look up.

    :return: The value in dict corresponding with the given key.
    """
    return dict[key]

@register.filter
def to_list(iterator):
    """
    Convert an object (e.g. a generator, or some other iterator) to a list.

    :param iterator: The iterator to convert.
    :return: The object converted into a list.
    """
    return list(iterator)
