from __future__ import print_function, unicode_literals, with_statement, division

from django.conf import settings as django_settings
from django_common.session import SessionManager


def common_settings(request):
    return {
        'domain_name': django_settings.DOMAIN_NAME,
        'www_root': django_settings.WWW_ROOT,
        'is_dev': django_settings.IS_DEV,
        'is_prod': django_settings.IS_PROD,
        'usertime': SessionManager(request).get_usertime()
    }
