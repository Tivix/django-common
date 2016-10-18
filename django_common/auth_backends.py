from __future__ import print_function, unicode_literals, with_statement, division

import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


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
            logging.warning('Unsuccessful login attempt using username/email: {0}'.format(username))

        return None
