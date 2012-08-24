=======================
django-common-helpers
=======================

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
		"common_settings",
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

Available fields:

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

- decimal field requires two more arguments max_digits and decimal_places, exmaple::
    
    decimal:total_cost:10:2

NOTICE: To all models scaffold automatically adds two fields: update_date and create_date.

4. How it works?

Scaffold creates models, views (CRUD), forms, templates, admin, urls and basic tests. Scaffold templates are using two blocks extending from base.html: 

{% extends "base.html" %}
{% block page-title %} {% endblock %} for title page
{% block conent %} for site content

So be sure you have your base.html set up properly.

Scaffold uses ajax forms 

5. Example usage

FULL EXAMPLE:

Let's create very simple ``forum`` app. We need Forum, Topic and Post model.

- Forum model

Forum model needs just one field ``name``::

    python manage.py scaffold forum --model Forum char:name

- Topic model

Topics are created by site users so we need: created_by, title and Forum foreign key (update_date and create_date are always added to models)::

    python manage.py scaffold forum --model Topic foreign:created_by:User char:title foreign:forum:Forum

- Post model

Last one are Posts. Posts are related to Topics. Here we need: title, body, created_by and foreign key to Topic::

    python manage.py scaffold forum --model Post char:title text:body foreign:created_by:User foreign:topic:Topic

All data should be in place!

Now you must add "forum" app to ``INSTALLED_APPS`` and include app in urls.py file by adding into urlpatterns::

    urlpatterns = patterns('',
        ...
        (r'^', include('forum.urls')),
    )

Now syncdb new app and you are ready to go::

    python manage.py syncdb

Run your server::

    python manage.py runserver

And go to forum main page::

    http://localhost:8000/forum/

All structure are in place. Now you can personalize models, templates and urls.

At the end you can test new app by runing test::

    python manage.py test forum

You should see no errors at all::

    Creating test database for alias 'default'...
    .......
    ----------------------------------------------------------------------
    Ran 7 tests in 0.884s

    OK

Happy scaffolding!

This open-source app is brought to you by Tivix, Inc. ( http://tivix.com/ )
