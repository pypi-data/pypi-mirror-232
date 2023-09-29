from django.urls import URLPattern, URLResolver
from django.urls import get_resolver


def list_urls(list, acc=None):
    if acc is None:
        acc = ''
    if not list:
        return
    l = list[0]
    str_pattern = str(l.pattern)
    match_pattern = not str_pattern.endswith('/(?P<pk>[^/.]+)/$') and \
                    (str_pattern.endswith('/$') or str_pattern.endswith('/'))
    if isinstance(l, URLPattern) and match_pattern:
        # l.callback tiene el view
        str_pattern = str_pattern.replace('^', '').replace('/$', '/').replace('(?P<pk>[/.]+)', '<pk>')
        yield f"/{acc}{str_pattern}"
    elif isinstance(l, URLResolver):
        yield from list_urls(l.url_patterns, f"{acc}{str(l.pattern)}")
    yield from list_urls(list[1:], acc)


def list_urlresolver(list):
    if not list:
        return
    r = list[0]
    if isinstance(r, URLResolver) and '.api.urls' in str(r.urlconf_module):
        yield r
    yield from list_urlresolver(list[1:])


def get_endpoints(exclude=None):
    urls_resolve = list(list_urlresolver(get_resolver().url_patterns))
    endpoints = list(list_urls(urls_resolve))
    if exclude:
        for endpoint in exclude:
            endpoints.remove(endpoint)
    return endpoints