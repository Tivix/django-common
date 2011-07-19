
class SessionManagerBase(object):
    """
    Base class that a "SessionManager" concrete class should extend. It should have a list called _SESSION_KEYS that
    lists all the keys that class uses/depends on.
    
    Ideally each app has a session.py that has this class and is used in the apps views etc.
    """
    def __init__(self, request, prepend_key_with=''):
        self._session = request.session
        self._prepend_key_with = prepend_key_with
  
    def _get_or_set(self, key, value):
        key = '%s%s' % (self._prepend_key_with, key)
        
        if not value is None:
            self._session[key] = value
            return value
        return self._session.get(key)
  
    def reset_keys(self):
        for key in self._SESSION_KEYS:
            key = '%s%s' % (self._prepend_key_with, key)
            
            if self._session.has_key(key):
                del self._session[key]
