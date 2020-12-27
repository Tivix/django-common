import os
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        dir_for_report = os.path.join(settings.BASE_DIR.parent, 'htmlcov')

        os.system("coverage run --source='.' --omit='manage.py' manage.py test")
        os.system('coverage html --directory="{}" --omit="manage.py wsgi.py asgi.py"'.format(dir_for_report))
