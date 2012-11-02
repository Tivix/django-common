from StringIO import StringIO

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect, Http404
from django.utils import simplejson


class JsonResponse(HttpResponse):
  def __init__(self, data={ }, errors=[ ], success=True):
    """
    data is a map, errors a list
    """
    json = json_response(data=data, errors=errors, success=success)
    super(JsonResponse, self).__init__(json, mimetype='application/json')

class JsonpResponse(HttpResponse):
  """
  Padded JSON response, used for widget XSS
  """
  def __init__(self, request, data={ }, errors=[ ], success=True):
    """
    data is a map, errors a list
    """
    json = json_response(data=data, errors=errors, success=success)
    js = "%s(%s)" % (request.GET.get("jsonp", "jsonp_callback"), json)
    super(JsonpResponse, self).__init__(js, mimetype='application/javascipt')

def json_response(data={ }, errors=[ ], success=True):
  data.update({
    'errors': errors,
    'success': len(errors) == 0 and success,
  })
  return simplejson.dumps(data)


class XMLResponse(HttpResponse):
  def __init__(self, data):
    """
    data is the entire xml body/document
    """
    super(XMLResponse, self).__init__(data, mimetype='text/xml')
