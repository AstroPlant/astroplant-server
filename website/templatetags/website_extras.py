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
