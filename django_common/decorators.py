from django.conf import settings
from django.http import HttpResponseRedirect


def ssl_required(allow_non_ssl=False):
    """Views decorated with this will always get redirected to https except when allow_non_ssl is set to true."""
    def wrapper(view_func):
        def _checkssl(request, *args, **kwargs):
            # allow_non_ssl=True lets non-https requests to come through to this view (and hence not redirect)
            if hasattr(settings, 'SSL_ENABLED') and settings.SSL_ENABLED and not request.is_secure() and not allow_non_ssl:
                return HttpResponseRedirect(request.build_absolute_uri().replace('http://', 'https://'))
            return view_func(request, *args, **kwargs)
        
        return _checkssl
    return wrapper
