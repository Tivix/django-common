from __future__ import print_function, unicode_literals, with_statement, division

import logging

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        """
        "username" being passed is really email address and being compared to as such.
        """
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            logging.warn('Unsuccessful login attempt using username/email: %s' % username)

        return None
