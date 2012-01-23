from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.cache import cache

from datetime import datetime
from optparse import make_option

from django_common.scaffold import Scaffold

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--app', default=None, dest='app', help='App name'),
        make_option('--model', default=None, dest='model', help='Model name'),
    )
    def handle(self, *args, **options):
        scaffold = Scaffold(options['app'], options['model'], args)
        scaffold.run()
        