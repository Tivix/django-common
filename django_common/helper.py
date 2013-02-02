"Some common routines that can be used throughout the code."
import hashlib, os, logging, re, datetime, threading

from django.http import Http404
from django.utils import simplejson
from django.utils.encoding import force_unicode
from django.template import Context, RequestContext
from django.template.loader import get_template
from django.core import exceptions

from django_common.tzinfo import utc, Pacific


class AppException(exceptions.ValidationError):
    """Base class for exceptions used in our system.

    A common base class permits application code to distinguish between exceptions raised in our code from ones raised
    in libraries.
    """
    pass

class InvalidContentType(AppException):
  def __init__(self, file_types, msg=None):
    msg = msg or 'Only the following file content types are permitted: %s' % str(file_types)
    super(self.__class__, self).__init__(msg)
    self.file_types = file_types

class FileTooLarge(AppException):
  def __init__(self, file_size_kb, msg=None):
    msg = msg or 'Files may not be larger than %s KB' % file_size_kb
    super(self.__class__, self).__init__(msg)
    self.file_size = file_size_kb

def is_among(value, *possibilities):
  "Ensure that the method that has been used for the request is one of the expected ones (e.g., GET or POST)."
  for possibility in possibilities:
    if value == possibility:
      return True
  raise Exception, 'A different request value was encountered than expected: %s' % value

def form_errors_serialize(form):
  errors = {}
  for field in form.fields.keys():
    if form.errors.has_key(field):
      if form.prefix:
          errors['%s-%s' % (form.prefix, field)] = force_unicode(form.errors[field])
      else:
          errors[field] = force_unicode(form.errors[field])
  
  if form.non_field_errors():
    errors['non_field_errors'] = force_unicode(form.non_field_errors())
  return {'errors': errors}

def json_response(data={ }, errors=[ ], success=True):
    data.update({
        'errors': errors,
        'success': len(errors) == 0 and success,
    })
    return simplejson.dumps(data)

def sha224_hash():
    return hashlib.sha224(os.urandom(224)).hexdigest()

def sha1_hash():
    return hashlib.sha1(os.urandom(224)).hexdigest()

def md5_hash(image=None, max_length=None):
    # TODO:  Figure out how much entropy is actually needed, and reduce the current number of bytes if possible if doing
    # so will result in a performance improvement.
    if max_length:
        assert max_length > 0

    ret = hashlib.md5(image or os.urandom(224)).hexdigest()
    return ret if not max_length else ret[:max_length]

def start_thread(target, *args):
   t = threading.Thread(target=target, args=args)
   t.setDaemon(True)
   t.start()

def send_mail(subject, message, from_email, recipient_emails, files = None, html=False, reply_to=None, bcc=None, cc=None):
  import django.core.mail
  try:
    logging.debug('Sending mail to: %s' % ', '.join(r for r in recipient_emails))
    logging.debug('Message: %s' % message)
    email = django.core.mail.EmailMessage(subject, message, from_email, recipient_emails, bcc, cc=cc)
    if html:
        email.content_subtype = "html"
    if files:
        for file in files:
            email.attach_file(file)
    if reply_to:
        email.extra_headers = {'Reply-To': reply_to}
    email.send()
        
  except Exception, e:
    # TODO:  Raise error again so that more information is included in the logs?
    logging.error('Error sending message [%s] from %s to %s %s' % (subject, from_email, recipient_emails, e))

def send_mail_in_thread(subject, message, from_email, recipient_emails, files = None, html=False, reply_to=None, bcc=None, cc=None):
    start_thread(send_mail, subject, message, from_email, recipient_emails, files, html, reply_to, bcc, cc)

def send_mail_using_template(subject, template_name, from_email, recipient_emails, context_map, in_thread=False, files = None, html=False, reply_to=None, bcc=None, cc=None):
    t = get_template(template_name)
    message = t.render(Context(context_map))
    if in_thread:
        return send_mail_in_thread(subject, message, from_email, recipient_emails, files, html, reply_to, bcc, cc)
    else:
        return send_mail(subject, message, from_email, recipient_emails, files, html, reply_to, bcc, cc)

def utc_to_pacific(timestamp):
    return timestamp.replace(tzinfo=utc).astimezone(Pacific)

def pacific_to_utc(timestamp):
    return timestamp.replace(tzinfo=Pacific).astimezone(utc)
    

def humanize_time_since(timestamp = None):
    """Returns a fuzzy time since. Will only return the largest time. EX: 20 days, 14 min"""

    timeDiff = datetime.datetime.now() - timestamp
    days = timeDiff.days
    hours = timeDiff.seconds/3600
    minutes = timeDiff.seconds%3600/60
    seconds = timeDiff.seconds%3600%60

    str = ""
    tStr = ""
    if days > 0:
        if days == 1:   tStr = "day"
        else:           tStr = "days"
        str = str + "%s %s" %(days, tStr)
        return str
    elif hours > 0:
        if hours == 1:  tStr = "hour"
        else:           tStr = "hours"
        str = str + "%s %s" %(hours, tStr)
        return str
    elif minutes > 0:
        if minutes == 1:tStr = "min"
        else:           tStr = "mins"           
        str = str + "%s %s" %(minutes, tStr)
        return str
    elif seconds > 0:
        if seconds == 1:tStr = "sec"
        else:           tStr = "secs"
        str = str + "%s %s" %(seconds, tStr)
        return str
    else:
        return str

def chunks(l, n):
    """ split successive n-sized chunks from a list."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]        

