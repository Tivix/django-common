from __future__ import print_function, unicode_literals, with_statement, division

import sys

from django.db import transaction

PY2 = sys.version_info[0] == 2

# commit_on_success was removed in 1.8, use atomic
if hasattr(transaction, 'atomic'):
    atomic_decorator = getattr(transaction, 'atomic')
else:
    atomic_decorator = getattr(transaction, 'commit_on_success')

if not PY2:
    string_types = (str,)
else:
    string_types = (str, unicode)
