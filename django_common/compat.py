from __future__ import print_function, unicode_literals, with_statement, division

import sys
from django import VERSION
from django.db import transaction
from django.utils import encoding

PY2 = sys.version_info[0] == 2

# commit_on_success was removed in 1.8, use atomic
if hasattr(transaction, 'atomic'):
    atomic_decorator = getattr(transaction, 'atomic')
else:
    atomic_decorator = getattr(transaction, 'commit_on_success')

# ugly hack required for Python 2/3 compat
if hasattr(encoding, 'force_unicode'):
    force_unicode = encoding.force_unicode
elif hasattr(encoding, 'force_text'):
    force_unicode = encoding.force_text
else:
    force_unicode = lambda x: x


if VERSION[1] >= 8:
    from django.contrib.admin.utils import unquote, flatten_fieldsets
else:
    from django.contrib.admin.util import unquote, flatten_fieldsets

if not PY2:
    string_types = (str,)
else:
    string_types = (str, unicode)
