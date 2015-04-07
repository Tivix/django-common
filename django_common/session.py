from __future__ import print_function, unicode_literals, with_statement, division

from datetime import datetime, timedelta
from django.conf import settings


class SessionManagerBase(object):
    """
    Base class that a "SessionManager" concrete class should extend.
    It should have a list called _SESSION_KEYS that lists all the keys that class uses/depends on.

    Ideally each app has a session.py that has this class and is used in the apps views etc.
    """
    def __init__(self, request, prepend_key_with=''):
        self._session = request.session
        self._prepend_key_with = prepend_key_with

    def _get_or_set(self, key, value):
        key = '{0}{1}'.format(self._prepend_key_with, key)

        if value is not None:
            self._session[key] = value
            return value
        return self._session.get(key)

    def reset_keys(self):
        for key in self._SESSION_KEYS:
            key = '{0}{1}'.format(self._prepend_key_with, key)

            if key in self._session:
                del self._session[key]


class SessionManager(SessionManagerBase):
    """Manages storing the cart"""

    USER_ONLINE_TIMEOUT = 180  # 3 min

    USERTIME = 'usertime'
    _GENERIC_VAR_KEY_PREFIX = 'lpvar_'   # handles generic stuff being stored in the session

    _SESSION_KEYS = [
        USERTIME,
    ]

    def __init__(self, request):
        super(SessionManager, self).__init__(request, prepend_key_with=request.get_host())
        if not self._get_or_set(self.USERTIME, None):
            self._get_or_set(self.USERTIME, None)

    def get_usertime(self):
        usertime = self._get_or_set(self.USERTIME, None)
        try:
            return usertime['last'] - usertime['start']
        except:
            return 0

    def ping_usertime(self):
        # Override default user online timeout
        try:
            timeout = int(settings.USER_ONLINE_TIMEOUT)
        except:
            timeout = self.USER_ONLINE_TIMEOUT
        if not self._get_or_set(self.USERTIME, None):
            self._get_or_set(self.USERTIME, {'start': datetime.now(), 'last': datetime.now()})
        else:
            usertime = self._get_or_set(self.USERTIME, None)
            if usertime['last'] + timedelta(seconds=timeout) < datetime.now():
                # This mean user reached timeout - we start from begining
                self._get_or_set(self.USERTIME, {'start': datetime.now(), 'last': datetime.now()})
            else:
                # We just update last time
                usertime['last'] = datetime.now()
        return self._get_or_set(self.USERTIME, None)

    def clear_usertime(self):
        return self._get_or_set(self.USERTIME, {})

    def generic_var(self, key, value=None):
        """
        Stores generic variables in the session prepending it with _GENERIC_VAR_KEY_PREFIX.
        """
        return self._get_or_set('{0}{1}'.format(self._GENERIC_VAR_KEY_PREFIX, key), value)
