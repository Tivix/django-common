"Some common routines that can be used throughout the code."
from __future__ import print_function, unicode_literals, with_statement, division

import hashlib
import os
import logging
import datetime
import threading

try:
    import json
except ImportError:
    from django.utils import simplejson as json
from django.utils.encoding import force_text
from django.template import Context
from django.template.loader import get_template
from django.core import exceptions

from django_common.tzinfo import utc, Pacific


class AppException(exceptions.ValidationError):
    """
    Base class for exceptions used in our system.

    A common base class permits application code to distinguish between exceptions raised in
    our code from ones raised in libraries.
    """
    pass


class InvalidContentType(AppException):
    def __init__(self, file_types, msg=None):
        if not msg:
            msg = 'Only the following file ' \
                  'content types are permitted: {0}'.format(str(file_types))
        super(self.__class__, self).__init__(msg)
        self.file_types = file_types


class FileTooLarge(AppException):
    def __init__(self, file_size_kb, msg=None):
        if not msg:
            msg = 'Files may not be larger than {0} KB'.format(file_size_kb)
        super(self.__class__, self).__init__(msg)
        self.file_size = file_size_kb


def get_class(kls):
    """
    Converts a string to a class.
    Courtesy:
    http://stackoverflow.com/q/452969/#452981
    """
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def is_among(value, *possibilities):
    """
    Ensure that the method that has been used for the request is one
    of the expected ones (e.g., GET or POST).
    """
    for possibility in possibilities:
        if value == possibility:
            return True
    raise Exception('A different request value was encountered than expected: {0}'.format(value))


def form_errors_serialize(form):
    errors = {}
    for field in form.fields.keys():
        if field in form.errors:
            if form.prefix:
                errors['{0}-{1}'.format(form.prefix, field)] = force_text(form.errors[field])
            else:
                errors[field] = force_text(form.errors[field])

    if form.non_field_errors():
        errors['non_field_errors'] = force_text(form.non_field_errors())
    return {'errors': errors}


def json_response(data=None, errors=None, success=True):
    if not errors:
        errors = []
    if not data:
        data = {}
    data.update({
        'errors': errors,
        'success': len(errors) == 0 and success,
    })
    return json.dumps(data)


def sha224_hash():
    return hashlib.sha224(os.urandom(224)).hexdigest()


def sha1_hash():
    return hashlib.sha1(os.urandom(224)).hexdigest()


def md5_hash(image=None, max_length=None):
    # TODO:  Figure out how much entropy is actually needed, and reduce the current number
    # of bytes if possible if doing so will result in a performance improvement.
    if max_length:
        assert max_length > 0

    ret = hashlib.md5(image or os.urandom(224)).hexdigest()
    return ret if not max_length else ret[:max_length]


def start_thread(target, *args):
    t = threading.Thread(target=target, args=args)
    t.setDaemon(True)
    t.start()


def send_mail(subject, message, from_email, recipient_emails, files=None,
              html=False, reply_to=None, bcc=None, cc=None, files_manually=None):
    """
    Sends email with advanced optional parameters

    To attach non-file content (e.g. content not saved on disk), use
    files_manually parameter and provide list of 3 element tuples, e.g.
    [('design.png', img_data, 'image/png'),] which will be passed to
    email.attach().
    """
    import django.core.mail
    try:
        logging.debug('Sending mail to: {0}'.format(', '.join(r for r in recipient_emails)))
        logging.debug('Message: {0}'.format(message))
        email = django.core.mail.EmailMessage(subject, message, from_email, recipient_emails,
                                              bcc, cc=cc)
        if html:
            email.content_subtype = "html"
        if files:
            for file in files:
                email.attach_file(file)
        if files_manually:
            for filename, content, mimetype in files_manually:
                email.attach(filename, content, mimetype)
        if reply_to:
            email.extra_headers = {'Reply-To': reply_to}
        email.send()
    except Exception as e:
        # TODO:  Raise error again so that more information is included in the logs?
        logging.error('Error sending message [{0}] from {1} to {2} {3}'.format(
            subject, from_email, recipient_emails, e))


def send_mail_in_thread(subject, message, from_email, recipient_emails, files=None, html=False,
                        reply_to=None, bcc=None, cc=None, files_manually=None):
    start_thread(send_mail, subject, message, from_email, recipient_emails, files, html,
                 reply_to, bcc, cc, files_manually)


def send_mail_using_template(subject, template_name, from_email, recipient_emails, context_map,
                             in_thread=False, files=None, html=False, reply_to=None, bcc=None,
                             cc=None, files_manually=None):
    t = get_template(template_name)
    message = t.render(context_map)
    if in_thread:
        return send_mail_in_thread(subject, message, from_email, recipient_emails, files, html,
                                   reply_to, bcc, cc, files_manually)
    else:
        return send_mail(subject, message, from_email, recipient_emails, files, html, reply_to,
                         bcc, cc, files_manually)


def utc_to_pacific(timestamp):
    return timestamp.replace(tzinfo=utc).astimezone(Pacific)


def pacific_to_utc(timestamp):
    return timestamp.replace(tzinfo=Pacific).astimezone(utc)


def humanize_time_since(timestamp=None):
    """
    Returns a fuzzy time since. Will only return the largest time. EX: 20 days, 14 min
    """
    timeDiff = datetime.datetime.now() - timestamp
    days = timeDiff.days
    hours = timeDiff.seconds / 3600
    minutes = timeDiff.seconds % 3600 / 60
    seconds = timeDiff.seconds % 3600 % 60

    str = ""
    if days > 0:
        if days == 1:
            t_str = "day"
        else:
            t_str = "days"
        str += "{0} {1}".format(days, t_str)
        return str
    elif hours > 0:
        if hours == 1:
            t_str = "hour"
        else:
            t_str = "hours"
        str += "{0} {1}".format(hours, t_str)
        return str
    elif minutes > 0:
        if minutes == 1:
            t_str = "min"
        else:
            t_str = "mins"
        str += "{0} {1}".format(minutes, t_str)
        return str
    elif seconds > 0:
        if seconds == 1:
            t_str = "sec"
        else:
            t_str = "secs"
        str += "{0} {1}".format(seconds, t_str)
        return str
    else:
        return str


def chunks(l, n):
    """
    split successive n-sized chunks from a list.
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]
