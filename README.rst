=====================
django-common-helpers
=====================


Overview
---------

Django-common consists of the following things:

	- A middleware that makes sure your web-app runs either on or without 'www' in the domain.

	- A ``SessionManagerBase`` base class, that helps in keeping your session related  code object-oriented and clean! See session.py for usage details.

	- An ``EmailBackend`` for authenticating users based on their email, apart from username.

	- Some custom db fields that you can use in your models including a ``UniqueHashField`` and ``RandomHashField``.

	- Bunch of helpful functions in helper.py

	- A ``render_form_field`` template tag that makes rendering form fields easy and DRY.

	- A couple of dry response classes: ``JsonResponse`` and ``XMLResponse`` in the django_common.http that can be used in views that give json/xml responses.


Installation
-------------

- Install django_common (ideally in your virtualenv!) using pip or simply getting a copy of the code and putting it in a directory in your codebase.

- Add ``django_common`` to your Django settings ``INSTALLED_APPS``::

	INSTALLED_APPS = [
        # ...
        "django_common",
    ]

- Add the following to your settings.py with appropriate values:

	- IS_DEV
	- IS_PROD
	- DOMAIN_NAME
	- WWW_ROOT

- Add ``common_settings`` to your Django settings ``TEMPLATE_CONTEXT_PROCESSORS``::

	TEMPLATE_CONTEXT_PROCESSORS = [
		# ...
		'django_common.context_processors.common_settings',
	]

- Add ``EmailBackend`` to the Django settings ``AUTHENTICATION_BACKENDS``::

	AUTHENTICATION_BACKENDS = (
		'django_common.auth_backends.EmailBackend',
		'django.contrib.auth.backends.ModelBackend'
	)

- Add ``WWWRedirectMiddleware`` if required to the list of middlewares::

	MIDDLEWARE_CLASSES = [
		# ...
		"WWWRedirectMiddleware",
	]

- Scaffolds / ajax_form.js (ajax forms) etc. require jQuery


Scaffolding feature
-------------------

1. Installing

To get scaffold just download ``scaffold`` branch of django-common, add it to ``INSTALLED_APPS`` and set up ``SCAFFOLD_APPS_DIR`` in settings.

Default is set to main app directory. However if you use django_base_project you must set up this to ``SCAFFOLD_APPS_DIR = 'apps/'``.

2. Run

To run scaffold type::

    python manage.py scaffold APPNAME --model MODELNAME [fields]

APPNAME is app name. If app does not exists it will be created.
MODELNAME is model name. Just enter model name that you want to create (for example: Blog, Topic, Post etc). It must be alphanumerical. Only one model per run is allowed!

[fields] - list of the model fields.

3. Field types

Available fields::

    char - CharField
    text - TextField
    int - IntegerFIeld
    decimal -DecimalField
    datetime - DateTimeField
    foreign - ForeignKey

All fields requires name that is provided after ``:`` sign, for example::

    char:title  text:body int:posts datetime:create_date

Two fields ``foreign`` and ``decimal`` requires additional parameters:

- "foreign" as third argument takes foreignkey model, example::

    foreign:blog:Blog, foreign:post:Post, foreign:added_by:User

NOTICE: All foreign key models must alread exist in project. User and Group model are imported automatically.

- decimal field requires two more arguments ``max_digits`` and ``decimal_places``, example::

    decimal:total_cost:10:2

NOTICE: To all models scaffold automatically adds two fields: update_date and create_date.

4. How it works?

Scaffold creates models, views (CRUD), forms, templates, admin, urls and basic tests (CRUD). Scaffold templates are using two blocks extending from base.html::

    {% extends "base.html" %}
    {% block page-title %} {% endblock %}
    {% block conent %} {% endblock %}

So be sure you have your base.html set up properly.

Scaffolding example usage
-------------------------

Let's create very simple ``forum`` app. We need ``Forum``, ``Topic`` and ``Post`` model.

- Forum model

Forum model needs just one field ``name``::

    python manage.py scaffold forum --model Forum char:name

- Topic model

Topics are created by site users so we need: ``created_by``, ``title`` and ``Forum`` foreign key (``update_date`` and ``create_date`` are always added to models)::

    python manage.py scaffold forum --model Topic foreign:created_by:User char:title foreign:forum:Forum

- Post model

Last one are Posts. Posts are related to Topics. Here we need: ``title``, ``body``, ``created_by`` and foreign key to ``Topic``::

    python manage.py scaffold forum --model Post char:title text:body foreign:created_by:User foreign:topic:Topic

All data should be in place!

Now you must add ``forum`` app to ``INSTALLED_APPS`` and include app in ``urls.py`` file by adding into urlpatterns::

    urlpatterns = [
        ...
        url(r'^', include('forum.urls')),
    ]

Now syncdb new app and you are ready to go::

    python manage.py syncdb

Run your server::

    python manage.py runserver

And go to forum main page::

    http://localhost:8000/forum/

All structure are in place. Now you can personalize models, templates and urls.

At the end you can test new app by runing test::

    python manage.py test forum

    Creating test database for alias 'default'...
    .......
    ----------------------------------------------------------------------
    Ran 7 tests in 0.884s

    OK

Happy scaffolding!

Generation of SECRET_KEY
------------------------

Sometimes you need to generate a new ``SECRET_KEY`` so now you can generate it using this command:

    $ python manage.py generate_secret_key

Sample output:

    $ python manage.py generate_secret_key

    SECRET_KEY: 7,=_3t?n@'wV=p`ITIA6"CUgJReZf?s:`f~Jtl#2i=i^z%rCp-

Optional arguments

1. ``--length`` - is the length of the key ``default=50``
2. ``--alphabet`` - is the alphabet to use to generate the key ``default=ascii letters + punctuation symbols``

Django settings keys
--------------------

- DOMAIN_NAME - Domain name, ``"www.example.com"``
- WWW_ROOT - Root website url, ``"https://www.example.com/"``
- IS_DEV - Current environment is development environment
- IS_PROD - Current environment is production environment


This open-source app is brought to you by Tivix, Inc. ( http://tivix.com/ )


Changelog
=========

0.9.0
-----
    - Django 1.10 support
    - README.txt invalid characters fix
    - Add support for custom user model in EmailBackend
    - Fixes for DB fields and management commands

0.8.0
-----
    - compatability code moved to compat.py
    - ``generate_secret_key`` management command.
    - Fix relating to https://code.djangoproject.com/ticket/17627, package name change.
    - Pass form fields with HiddenInput widget through render_form_field
    - string.format usage / other refactoring / more support for Python 3


0.7.0
-----
    - PEP8 codebase cleanup.
    - Improved python3 support.
    - Django 1.8 support.

0.6.4
-----
    - Added python3 support.

0.6.3
-----
    - Changed mimetype to content_type in class JsonReponse to reflect Django 1.7 deprecation.

0.6.2
-----
    - Django 1.7 compatability using simplejson as fallback


0.6.1
-----
    - Added support for attaching content to emails manually (without providing path to file).

    - Added LoginRequiredMixin


0.6
---
    - Added support for Django 1.5

    - Added fixes in nested inlines

    - Added support for a multi-select checkbox field template and radio button in render_form_field

    - Added Test Email Backend for overwrite TO, CC and BCC fields in all outgoing emails

    - Added Custom File Email Backend to save emails as file with custom extension

    - Rewrote fragments to be Bootstrap-compatible


0.5.1
-----

    - root_path deprecated in Django 1.4+


0.5
---

    - Added self.get_inline_instances() usages instead of self.inline_instances

    - Changed minimum requirement to Django 1.4+ because of the above.


0.4
---

    - Added nested inline templates, js and full ajax support. Now we can add/remove nested fields dynamically.

    - JsonpResponse object for padded JSON

    - User time tracking feature - how long the user has been on site, associated middleware etc.

    - @anonymous_required decorator: for views that should not be accessed by a logged-in user.

    - Added EncryptedTextField and EncryptedCharField

    - Misc. bug fixes
