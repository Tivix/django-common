from __future__ import print_function, unicode_literals, with_statement, division

from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext as _

import string


class Command(BaseCommand):
    help = _('This command generates SECRET_KEY')

    # Default length is 50
    length = 50

    # Allowed characters
    allowed_chars = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation

    def add_arguments(self, parser):
        """
        Define optional arguments with default values
        """
        parser.add_argument('--length', default=self.length,
                            type=int, help=_('SECRET_KEY length default=%d' % self.length))

        parser.add_argument('--alphabet', default=self.allowed_chars,
                            type=str, help=_('alphabet to use default=%s' % self.allowed_chars))

    def handle(self, *args, **options):
        length = options.get('length')
        alphabet = options.get('alphabet')
        secret_key = str(get_random_string(length=length, allowed_chars=alphabet))

        print('SECRET_KEY: %s' % secret_key)
