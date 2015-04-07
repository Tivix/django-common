from __future__ import print_function, unicode_literals, with_statement, division

import os

from django.conf import settings

from django.core.mail.backends.smtp import EmailBackend
from django.core.mail.backends.filebased import EmailBackend as FileEmailBackend
from django.core.mail import message


class TestEmailBackend(EmailBackend):
    """
        Email Backend to overwrite TO, CC and BCC in all outgoing emails to custom
        values.

        Sample values from setting.py:
        EMAIL_BACKEND = 'django_common.email_backends.TestEmailBackend'
        TEST_EMAIL_TO = ['dev@tivix.com']  # default are addresses form ADMINS
        TEST_EMAIL_CC = ['dev-cc@tivix.com']  # default is empty list
        TEST_EMAIL_BCC = ['dev-bcc@tivix.com']  # default is empty list
    """

    def _send(self, email_message):
        """A helper method that does the actual sending."""
        if not email_message.recipients():
            return False
        from_email = email_message.from_email
        if hasattr(message, 'sanitize_address'):
            from_email = message.sanitize_address(email_message.from_email,
                                                  email_message.encoding)
        if hasattr(settings, 'TEST_EMAIL_TO'):
            email_message.to = settings.TEST_EMAIL_TO
        else:
            email_message.to = dict(getattr(settings, 'ADMINS', ())).values()
        email_message.cc = getattr(settings, 'TEST_EMAIL_CC', [])
        email_message.bcc = getattr(settings, 'TEST_EMAIL_BCC', [])
        if hasattr(message, 'sanitize_address'):
            recipients = [message.sanitize_address(addr, email_message.encoding)
                          for addr in email_message.recipients()]
        else:
            recipients = email_message.recipients()
        try:
            self.connection.sendmail(from_email, recipients,
                                     email_message.message().as_string())
        except:
            if not self.fail_silently:
                raise
            return False
        return True


class CustomFileEmailBackend(FileEmailBackend):
    """
        Email Backend to save emails as file with custom extension. It makes easier
        to open emails in email applications, f.e. with eml extension for mozilla
        thunderbird.

        Sample values from setting.py:
        EMAIL_BACKEND = 'django_common.email_backends.CustomFileEmailBackend'
        EMAIL_FILE_PATH = '/email/file/path/'
        EMAIL_FILE_EXT = 'eml'
    """

    def _get_filename(self):
        filename = super(CustomFileEmailBackend, self)._get_filename()
        if hasattr(settings, 'EMAIL_FILE_EXT'):
            filename = '{0}.{1}'.format(os.path.splitext(filename)[0],
                                        settings.EMAIL_FILE_EXT.strip('.'))
        return filename
