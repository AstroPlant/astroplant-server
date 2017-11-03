from django import template
from django.core.urlresolvers import resolve

register = template.Library()

@register.simple_tag
def navigation_active(request, urls):
    r = resolve(request.path_info)
    name = "%s:%s" % (r.namespace, r.url_name)
    if name in urls.split():
        return "active"
    return ""
    