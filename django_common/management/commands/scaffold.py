from django.core.management.base import BaseCommand

from optparse import make_option

from django_common.scaffold import Scaffold
from django_common import settings


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--model', default=None, dest='model', help='Model name'),
    )

    def handle(self, *args, **options):
        if len(args) == 0:
            print "You must provide app name. For example:\n\npython manage.py scallfold my_app\n"
            return
        scaffold = Scaffold(args[0], options['model'], args)
        scaffold.run()

    def get_version(self):
        return 'django-common version: %s' % settings.VERSION
