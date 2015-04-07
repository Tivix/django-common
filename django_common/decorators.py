from __future__ import print_function, unicode_literals, with_statement, division

try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps

import inspect

from django.conf import settings
from django.http import HttpResponseRedirect


def ssl_required(allow_non_ssl=False):
    """
    Views decorated with this will always get redirected to https
    except when allow_non_ssl is set to true.
    """
    def wrapper(view_func):
        def _checkssl(request, *args, **kwargs):
            # allow_non_ssl=True lets non-https requests to come
            # through to this view (and hence not redirect)
            if hasattr(settings, 'SSL_ENABLED') and settings.SSL_ENABLED \
                    and not request.is_secure() and not allow_non_ssl:
                return HttpResponseRedirect(
                    request.build_absolute_uri().replace('http://', 'https://'))
            return view_func(request, *args, **kwargs)

        return _checkssl
    return wrapper


def disable_for_loaddata(signal_handler):
    """
    See: https://code.djangoproject.com/ticket/8399
    Disables signal from firing if its caused because of loaddata
    """
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        for fr in inspect.stack():
            if inspect.getmodulename(fr[1]) == 'loaddata':
                return
        signal_handler(*args, **kwargs)
    return wrapper


def anonymous_required(view, redirect_to=None):
    """
    Only allow if user is NOT authenticated.
    """
    if redirect_to is None:
        redirect_to = settings.LOGIN_REDIRECT_URL

    @wraps(view)
    def wrapper(request, *a, **k):
        if request.user and request.user.is_authenticated():
            return HttpResponseRedirect(redirect_to)
        return view(request, *a, **k)
    return wrapper
