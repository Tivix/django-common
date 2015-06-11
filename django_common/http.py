from __future__ import print_function, unicode_literals, with_statement, division

from django.http import HttpResponse

try:
    import json
except ImportError:
    from django.utils import simplejson as json


class JsonResponse(HttpResponse):
    def __init__(self, data=None, errors=None, success=True):
        """
        data is a map, errors a list
        """
        if not errors:
            errors = []
        if not data:
            data = {}
        json_resp = json_response(data=data, errors=errors, success=success)
        super(JsonResponse, self).__init__(json_resp, content_type='application/json')


class JsonpResponse(HttpResponse):
    """
    Padded JSON response, used for widget XSS
    """
    def __init__(self, request, data=None, errors=None, success=True):
        """
        data is a map, errors a list
        """
        if not errors:
            errors = []
        if not data:
            data = {}
        json_resp = json_response(data=data, errors=errors, success=success)
        js = "{0}({1})".format(request.GET.get("jsonp", "jsonp_callback"), json_resp)
        super(JsonpResponse, self).__init__(js, mimetype='application/javascipt')


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


class XMLResponse(HttpResponse):
    def __init__(self, data):
        """
        data is the entire xml body/document
        """
        super(XMLResponse, self).__init__(data, mimetype='text/xml')
