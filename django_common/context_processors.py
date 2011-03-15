from django.conf import settings as django_settings


def common_settings(request):
    return {
        'domain_name': django_settings.DOMAIN_NAME,
        'www_root': django_settings.WWW_ROOT,
        
        'is_dev': django_settings.IS_DEV,
        'is_prod': django_settings.IS_PROD,
    }
