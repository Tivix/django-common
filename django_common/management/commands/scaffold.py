from __future__ import print_function, unicode_literals, with_statement, division

from django.core.management.base import BaseCommand

from django_common.scaffold import Scaffold
from django_common import settings


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('app_name', nargs='*')
        parser.add_argument(
            '--model', default=None, dest='model', nargs='+', help="""
            model name - only one model name per run is allowed. \n
            It requires additional fields parameters:

            char - CharField \t\t\t\t
            text - TextField \t\t\t\t
            int - IntegerFIeld \t\t\t\t
            decimal -DecimalField \t\t\t\t
            datetime - DateTimeField \t\t\t\t
            foreign - ForeignKey \t\t\t\t

            Example usages: \t\t\t\t

                --model forum char:title  text:body int:posts datetime:create_date \t\t
                --model blog foreign:blog:Blog, foreign:post:Post, foreign:added_by:User \t\t
                --model finance decimal:total_cost:10:2

            """
        )

    def handle(self, *args, **options):
        if len(options['app_name']) == 0:
            print("You must provide app name. For example:\n\npython manage.py scallfold my_app\n")
            return

        app_name = options['app_name'][0]
        model_data = options['model']
        if model_data:
            model_name = model_data[0]
            fields = model_data[1:]
        else:
            model_name = None
            fields = None

        scaffold = Scaffold(app_name, model_name, fields)
        scaffold.run()

    def get_version(self):
        return 'django-common version: {0}'.format(settings.VERSION)
