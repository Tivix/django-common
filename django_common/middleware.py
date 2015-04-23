from __future__ import print_function, unicode_literals, with_statement, division

from django.conf import settings
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django_common.session import SessionManager

WWW = 'www'


class WWWRedirectMiddleware(object):
    """
    Redirect requests for example from http://www.mysirw.com/* to http://mysite.com/*
    """
    def process_request(self, request):
        if settings.IS_PROD and request.get_host() != settings.DOMAIN_NAME:
            proto_suffix = 's' if request.is_secure() else ''
            url = 'http{0}://{1}{2}'.format(proto_suffix, settings.DOMAIN_NAME,
                                            request.get_full_path())
            return HttpResponsePermanentRedirect(url)
        return None


class UserTimeTrackingMiddleware(object):
    """
    Tracking time user have been on site
    """
    def process_request(self, request):
        if request.user and request.user.is_authenticated():
            SessionManager(request).ping_usertime()
        else:
            SessionManager(request).clear_usertime()


class SSLRedirectMiddleware(object):
    """
    Redirects all the requests that are non SSL to a SSL url
    """
    def process_request(self, request):
        if not request.is_secure():
            url = 'https://{0}{1}'.format(settings.DOMAIN_NAME, request.get_full_path())
            return HttpResponseRedirect(url)
        return None


class NoSSLRedirectMiddleware(object):
    """
    Redirects if a non-SSL required view is hit. This middleware assumes a SSL protected view
    has been decorated by the 'ssl_required' decorator (see decorators.py)

    Redirects to https for admin though only for PROD
    """
    __DECORATOR_INNER_FUNC_NAME = '_checkssl'

    def __is_in_admin(self, request):
        return True if request.path.startswith('/admin/') else False

    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_func.func_name != self.__DECORATOR_INNER_FUNC_NAME \
                and not (self.__is_in_admin(request) and settings.IS_PROD) \
                and request.is_secure():  # request is secure, but view is not decorated
            url = 'http://{0}{1}'.format(settings.DOMAIN_NAME, request.get_full_path())
            return HttpResponseRedirect(url)
        elif self.__is_in_admin(request) and not request.is_secure() and settings.IS_PROD:
            url = 'https://{0}{1}'.format(settings.DOMAIN_NAME, request.get_full_path())
            return HttpResponseRedirect(url)
