=============
django-common
=============

Overview
--------

Django-common consists of the following things:
	
	- A middleware that makes sure your web-app runs either on or without 'www' in the domain.
	
	- A ``SessionManagerBase`` base class, that helps in keeping your session related  code object-oriented and clean! See session.py for usage details.
	
	- Some custom db fields that you can use in your models including a ``UniqueHashField`` and ``RandomHashField``.
	
	- Bunch of helpful functions in helper.py
	
	- A ``render_form_field`` template tag that makes rendering form fields easy and DRY.
	
	- A couple of dry response classes: ``JsonResponse`` and ``XMLResponse`` in the django_common.http that can be used in views that give json/xml responses.


Installation
------------

- Install django_common (ideally in your virtualenv!) using pip or simply getting a copy of the code and putting it in a
directory in your codebase.

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
		"common_settings",
	]

- Add ``WWWRedirectMiddleware`` if required to the list of middlewares::
	
	MIDDLEWARE_CLASSES = [
		# ...
		"WWWRedirectMiddleware",
	]


This open-source app is brought to you by Tivix, Inc. ( http://tivix.com/ )
