from __future__ import print_function, unicode_literals, with_statement, division

from os import path, system, listdir, sys, mkdir
from django.conf import settings
# VIEW CONSTS

LIST_VIEW = """
from %(app)s.forms import %(model)sForm
def %(lower_model)s_list(request, template='%(lower_model)s/list.html'):
    d = {}
    d['form'] = %(model)sForm()
    if request.method == 'POST':
        form = %(model)sForm(request.POST)
        if form.is_valid():
            item = form.save()
            return JsonResponse(data={'id': item.id, 'name': str(item), 'form': %(model)sForm().as_p(), 'token': get_token(request)})
        else:
            d['form'] = form
            return JsonResponse(data={'form': d['form'].as_p(), 'token': get_token(request)}, success=False)
    d['%(lower_model)s_list'] = %(model)s.objects.all()
    return render(request, template, d)
"""

DETAILS_VIEW = """
from %(app)s.forms import %(model)sForm
def %(lower_model)s_details(request, id, template='%(lower_model)s/details.html'):
    d = {}
    item = get_object_or_404(%(model)s, pk=id)
    d['form'] = %(model)sForm(instance=item)
    if request.method == 'POST':
        form = %(model)sForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            return JsonResponse(data={'form': %(model)sForm(instance=item).as_p(), 'token': get_token(request)})
        else:
            d['form'] = form
            return JsonResponse(data={'form': d['form'].as_p(), 'token': get_token(request)}, success=False)
    d['%(lower_model)s'] = %(model)s.objects.get(pk=id)
    return render(request, template, d)
"""

DELETE_VIEW = """
def %(lower_model)s_delete(request, id):
    item = %(model)s.objects.get(pk=id)
    item.delete()
    return JsonResponse()
"""
# MODELS CONSTS

MODEL_TEMPLATE = """
class %s(models.Model):
    %s
    update_date = models.DateTimeField(auto_now=True)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']
"""

IMPORT_MODEL_TEMPLATE = """from %(app)s.models import %(model)s"""

CHARFIELD_TEMPLATE = """
    %(name)s = models.CharField(max_length=%(length)s, null=%(null)s, blank=%(null)s)
"""

TEXTFIELD_TEMPLATE = """
    %(name)s = models.TextField(null=%(null)s, blank=%(null)s)
"""

INTEGERFIELD_TEMPLATE = """
    %(name)s = models.IntegerField(null=%(null)s, default=%(default)s)
"""

DECIMALFIELD_TEMPLATE = """
    %(name)s = models.DecimalField(max_digits=%(digits)s, decimal_places=%(places)s, null=%(null)s, default=%(default)s)
"""

DATETIMEFIELD_TEMPLATE = """
    %(name)s = models.DateTimeField(null=%(null)s, default=%(default)s)
"""

FOREIGNFIELD_TEMPLATE = """
    %(name)s = models.ForeignKey(%(foreign)s, null=%(null)s, blank=%(null)s)
"""

TEMPLATE_LIST_CONTENT = """
{%% extends "base.html" %%}

{%% block page-title %%}%(title)s{%% endblock %%}

{%% block content %%}
    <h1>%(model)s list</h1><br />
    <table style="border: solid 1px gray; width: 300px; text-align: center;" id="item-list">
        <tr style="background-color: #DDD">
            <th style="padding: 10px;">ID</th>
            <th>Name</th>
            <th>Action</th>
        </tr>
    {%% for item in %(model)s_list %%}
        <tr>
            <td style="padding: 10px;">{{ item.id }}</td>
            <td>{{ item }}</td>
            <td><a href="{%% url '%(model)s-details' item.id %%}">show</a></td>
        </tr>
    {%% endfor %%}
    </table>
    <br />
    <input type="button" onclick="$('#add-form-div').toggle();" value="Add new %(model)s"><br /><br />
    <div id="add-form-div" style="display: none;">
        <form action="{%% url '%(model)s-list' %%}" method="POST" id="add-form">
                <div id="form-fields">
                    {%% csrf_token %%}
                    {{ form }}
                </div>
                <input type="submit" value="Submit" />
        </form>
    </div>

    <script type="text/javascript">
        (new FormHelper('add-form')).bind_for_ajax(
            function(data) {
                $('#item-list').append('<td style="padding: 10px;">' + data.id + '</td><td>' + data.name + '</td><td><a href="{%% url %(model)s-list %%}' + data.id + '/">show</a></td>').hide().fadeIn();
                $('#form-fields').html('');
                $('#form-fields').append('<input type="hidden" value="' + data.token + '" name="csrfmiddlewaretoken">');
                $('#form-fields').append(data.form);
                $('#add-form-div').toggle();
            },
            function(data) {
                $('#form-fields').html('');
                $('#form-fields').append('<input type="hidden" value="' + data.token + '" name="csrfmiddlewaretoken">');
                $('#form-fields').append(data.form).hide().fadeIn();
                $('#add-form input[type=submit]').removeAttr('disabled');
            }
        );
    </script>
{%% endblock %%}
"""

TEMPLATE_DETAILS_CONTENT = """
{%% extends "base.html" %%}

{%% block page-title %%}%(title)s - {{ %(model)s }} {%% endblock %%}

{%% block content %%}
    <div class="item">
        <h1>%(model)s - {{ %(model)s }} </h1><br />
        <table style="border: solid 1px gray; width: 300px; text-align: center;" id="item-list">
            <tr style="background-color: #DDD">
                <th style="padding: 10px;">ID</th>
                <th>Name</th>
                <th>Action</th>
            </tr>
            <tr>
                <td style="padding: 10px;">{{ %(model)s.id }}</td>
                <td>{{ %(model)s }}</td>
                <td><input type="button" href="{%% url '%(model)s-delete' %(model)s.id %%}" id="delete-item" value="delete" /></td>
            </tr>
        </table>
        <br />
        <br />
        <br />
        <input type="button" onclick="$('#add-form-div').toggle();" value="Edit %(model)s"><br /><br />
        <div id="add-form-div" style="display: none;">
            <form action="{%% url '%(model)s-details' %(model)s.id %%}" method="POST" id="add-form">
                    <div id="form-fields">
                        {%% csrf_token %%}
                        {{ form }}
                    </div>
                    <input type="submit" value="Submit" />
            </form>
        </div>
    </div>

    <script type="text/javascript">
        (new FormHelper('add-form')).bind_for_ajax(
            function(data) {
                $('#form-fields').html('');
                $('#form-fields').append('<input type="hidden" value="' + data.token + '" name="csrfmiddlewaretoken">');
                $('#form-fields').append(data.form).hide().fadeIn();
                $('#add-form input[type=submit]').removeAttr('disabled');
            },
            function(data) {
                $('#form-fields').html('');
                $('#form-fields').append('<input type="hidden" value="' + data.token + '" name="csrfmiddlewaretoken">');
                $('#form-fields').append(data.form).hide().fadeIn();
                $('#add-form input[type=submit]').removeAttr('disabled');
            }
        );
        $('#delete-item').click(function() {
            $.get($(this).attr('href'), function(data) {
                $('div.item').before('<h1>Item removed</h1><br /><br />');
                $('div.item').remove();
            });
        });
    </script>
    <a href="{%% url '%(model)s-list' %%}">back to list</a>
{%% endblock %%}
"""

URL_CONTENT = """
from django.conf.urls import url
from django.contrib.auth import views as auth_views

from %(app)s import views

urlpatterns = [
    url(r'^%(model)s/$', views.%(model)s_list, name='%(model)s-list'),
    url(r'^%(model)s/(?P<id>\d+)/$', views.%(model)s_details, name='%(model)s-details'),
    url(r'^%(model)s/(?P<id>\d+)/delete/$', views.%(model)s_delete, name='%(model)s-delete'),
]
"""

URL_EXISTS_CONTENT = """
    url(r'^%(model)s/$', views.%(model)s_list, name='%(model)s-list'),
    url(r'^%(model)s/(?P<id>\d+)/$', views.%(model)s_details, name='%(model)s-details'),
    url(r'^%(model)s/(?P<id>\d+)/delete/$', views.%(model)s_delete, name='%(model)s-delete'),
"""

ADMIN_CONTENT = """
from %(app)s.models import %(model)s
admin.site.register(%(model)s)
"""

FORM_CONTENT = """

from %(app)s.models import %(model)s

class %(model)sForm(forms.ModelForm):
    class Meta:
        model = %(model)s
"""

TESTS_CONTENT = """

from %(app)s.models import %(model)s


class %(model)sTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test_user')

    def tearDown(self):
        self.user.delete()

    def test_list(self):
        response = self.client.get(reverse('%(lower_model)s-list'))
        self.failUnlessEqual(response.status_code, 200)

    def test_crud(self):
        # Create new instance
        response = self.client.post(reverse('%(lower_model)s-list'), {})
        self.assertContains(response, '"success": true')

        # Read instance
        items = %(model)s.objects.all()
        self.failUnlessEqual(items.count(), 1)
        item = items[0]
        response = self.client.get(reverse('%(lower_model)s-details', kwargs={'id': item.id}))
        self.failUnlessEqual(response.status_code, 200)

        # Update instance
        response = self.client.post(reverse('%(lower_model)s-details', kwargs={'id': item.id}), {})
        self.assertContains(response, '"success": true')

        # Delete instance
        response = self.client.post(reverse('%(lower_model)s-delete', kwargs={'id': item.id}), {})
        self.assertContains(response, '"success": true')
        items = %(model)s.objects.all()
        self.failUnlessEqual(items.count(), 0)

"""


class Scaffold(object):
    def _info(self, msg, indent=0):
        print("{0} {1}".format("\t" * int(indent), msg))

    def __init__(self, app, model, fields):
        self.app = app
        self.model = model
        self.fields = fields

        try:
            self.SCAFFOLD_APPS_DIR = settings.SCAFFOLD_APPS_DIR
        except:
            self.SCAFFOLD_APPS_DIR = './'

    def get_import(self, model):
        for dir in listdir(self.SCAFFOLD_APPS_DIR):
            if path.isdir('{0}{1}'.format(self.SCAFFOLD_APPS_DIR, dir)) \
                    and path.exists('{0}{1}/models.py'.format(self.SCAFFOLD_APPS_DIR, dir)):
                with open('{0}{1}/models.py'.format(self.SCAFFOLD_APPS_DIR, dir), 'r') as fp:
                    # Check if model exists
                    for line in fp.readlines():
                        if 'class {0}(models.Model)'.format(model) in line:
                            # print "Foreign key '%s' was found in app %s..." % (model, dir)
                            return IMPORT_MODEL_TEMPLATE % {'app': dir, 'model': model}
        return None

    def is_imported(self, path, model):
        with open(path, 'r') as import_file:
            for line in import_file.readlines():
                if 'import {0}'.format(model) in line:
                    # print "Foreign key '%s' was found in models.py..." % (foreign)
                    return True
        return False

    def add_global_view_imports(self, path):
        # from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
        import_list = list()

        with open(path, 'r') as import_file:
            need_import_shortcut = True
            need_import_urlresolvers = True
            need_import_users = True
            need_import_token = True
            need_import_JsonResponse = True

            for line in import_file.readlines():
                if 'from django.shortcuts import render, redirect, get_object_or_404' in line:
                    need_import_shortcut = False

                if 'from django.core.urlresolvers import reverse' in line:
                    need_import_urlresolvers = False

                if 'from django.contrib.auth.models import User, Group' in line:
                    need_import_users = False

                if 'from django.middleware.csrf import get_token' in line:
                    need_import_token = False

                if 'from django_common.http import JsonResponse' in line:
                    need_import_JsonResponse = False

            if need_import_shortcut:
                import_list.append(
                    'from django.shortcuts import render, redirect, get_object_or_404')
            if need_import_urlresolvers:
                import_list.append('from django.core.urlresolvers import reverse')
            if need_import_users:
                import_list.append('from django.contrib.auth.models import User, Group')
            if need_import_token:
                import_list.append('from django.middleware.csrf import get_token')
            if need_import_JsonResponse:
                import_list.append('from django_common.http import JsonResponse')

        return import_list

    def view_exists(self, path, view):
        # Check if view already exists
        with open(path, 'r') as view_file:
            for line in view_file.readlines():
                if 'def {0}('.format(view) in line:
                    return True
        return False

    def get_field(self, field):
        field = field.split(':')
        field_type = field[0]

        if field_type.lower() == 'char':
            try:
                length = field[2]
            except IndexError:
                length = 255

            try:
                null = field[3]
                null = 'False'
            except IndexError:
                null = 'True'

            return CHARFIELD_TEMPLATE % {'name': field[1], 'length': length, 'null': null}
        elif field_type.lower() == 'text':
            try:
                null = field[2]
                null = 'False'
            except IndexError:
                null = 'True'

            return TEXTFIELD_TEMPLATE % {'name': field[1], 'null': null}
        elif field_type.lower() == 'int':
            try:
                null = field[2]
                null = 'False'
            except IndexError:
                null = 'True'

            try:
                default = field[3]
            except IndexError:
                default = None

            return INTEGERFIELD_TEMPLATE % {'name': field[1], 'null': null, 'default': default}
        elif field_type.lower() == 'decimal':
            try:
                null = field[4]
                null = 'False'
            except IndexError:
                null = 'True'

            try:
                default = field[5]
            except IndexError:
                default = None

            return DECIMALFIELD_TEMPLATE % {
                'name': field[1],
                'digits': field[2],
                'places': field[3],
                'null': null,
                'default': default,
            }
        elif field_type.lower() == 'datetime':
            try:
                null = field[2]
                null = 'False'
            except IndexError:
                null = 'True'

            try:
                default = field[3]
            except IndexError:
                default = None

            return DATETIMEFIELD_TEMPLATE % {'name': field[1], 'null': null, 'default': default}
        elif field_type.lower() == 'foreign':
            foreign = field[2]
            name = field[1]
            # Check if this foreign key is already in models.py
            if foreign in ('User', 'Group'):
                if not self.is_imported('{0}{1}/models.py'.format(self.SCAFFOLD_APPS_DIR,
                                                                  self.app), foreign):
                    self.imports.append('\nfrom django.contrib.auth.models import User, Group\n')
                return FOREIGNFIELD_TEMPLATE % {'name': name, 'foreign': foreign, 'null': 'True'}
            if self.is_imported('{0}{1}/models.py'.format(
                    self.SCAFFOLD_APPS_DIR, self.app), foreign):
                return FOREIGNFIELD_TEMPLATE % {'name': name, 'foreign': foreign, 'null': 'True'}
            # Check imports
            if self.get_import(foreign):
                self.imports.append(self.get_import(foreign))
                return FOREIGNFIELD_TEMPLATE % {'name': name, 'foreign': foreign, 'null': 'True'}

            self._info('error\t{0}{1}/models.py\t{2} class not found'.format(
                self.SCAFFOLD_APPS_DIR, self.app, foreign), 1)
            return None

    def create_app(self):
        self._info("    App    ")
        self._info("===========")
        if self.SCAFFOLD_APPS_DIR and not path.exists('{0}'.format(self.SCAFFOLD_APPS_DIR)):
            raise Exception(
                "SCAFFOLD_APPS_DIR {0} does not exists".format(self.SCAFFOLD_APPS_DIR))
        if not path.exists('{0}{1}'.format(self.SCAFFOLD_APPS_DIR, self.app)):
            system('python manage.py startapp {0}'.format(self.app))
            system('mv {0} {1}{2}'.format(self.app, self.SCAFFOLD_APPS_DIR, self.app))
            self._info("create\t{0}{1}".format(self.SCAFFOLD_APPS_DIR, self.app), 1)
        else:
            self._info("exists\t{0}{1}".format(self.SCAFFOLD_APPS_DIR, self.app), 1)

    def create_views(self):
        self._info("   Views   ")
        self._info("===========")
        # Open models.py to read
        view_path = '{0}{1}/views.py'.format(self.SCAFFOLD_APPS_DIR, self.app)

        # Check if urls.py exists
        if path.exists('{0}{1}/views.py'.format(self.SCAFFOLD_APPS_DIR, self.app)):
            self._info('exists\t{0}{1}/views.py'.format(self.SCAFFOLD_APPS_DIR, self.app), 1)
        else:
            with open("{0}{1}/views.py".format(self.SCAFFOLD_APPS_DIR, self.app), 'w'):
                self._info('create\t{0}{1}/views.py'.format(self.SCAFFOLD_APPS_DIR, self.app), 1)

        import_list = list()
        view_list = list()

        # Add global imports
        import_list.append('\n'.join(imp for imp in self.add_global_view_imports(view_path)))

        # Add model imports
        if not self.is_imported(view_path, self.model):
            import_list.append(self.get_import(self.model))

        lower_model = self.model.lower()

        # Check if view already exists
        if not self.view_exists(view_path, "{0}_list".format(lower_model)):
            view_list.append(LIST_VIEW % {
                'lower_model': lower_model,
                'model': self.model,
                'app': self.app,
            })
            self._info("added \t{0}\t{1}_view".format(view_path, lower_model), 1)
        else:
            self._info("exists\t{0}\t{1}_view".format(view_path, lower_model), 1)

        if not self.view_exists(view_path, "{0}_details".format(lower_model)):
            view_list.append(DETAILS_VIEW % {
                'lower_model': lower_model,
                'model': self.model,
                'app': self.app,
            })
            self._info("added \t{0}\t{1}_details".format(view_path, lower_model), 1)
        else:
            self._info("exists\t{0}\t{1}_details".format(view_path, lower_model), 1)

        if not self.view_exists(view_path, "{0}_delete".format(lower_model)):
            view_list.append(DELETE_VIEW % {
                'lower_model': lower_model,
                'model': self.model,
            })
            self._info("added \t{0}\t{1}_delete".format(view_path, lower_model), 1)
        else:
            self._info("exists\t{0}\t{1}_delete".format(view_path, lower_model), 1)

        # Open views.py to append
        with open(view_path, 'a') as view_file:
            view_file.write('\n'.join([import_line for import_line in import_list]))
            view_file.write(''.join([view for view in view_list]))

    def create_model(self):
        self._info("   Model   ")
        self._info("===========")

        # Open models.py to read
        with open('{0}{1}/models.py'.format(self.SCAFFOLD_APPS_DIR, self.app), 'r') as fp:
            self.models_file = fp

            # Check if model already exists
            for line in self.models_file.readlines():
                if 'class {0}'.format(self.model) in line:
                    self._info('exists\t{0}{1}/models.py'.format(self.SCAFFOLD_APPS_DIR, self.app), 1)
                    return

            self._info('create\t{0}{1}/models.py'.format(self.SCAFFOLD_APPS_DIR, self.app), 1)

            # Prepare fields
            self.imports = []
            fields = []

            for field in self.fields:
                new_field = self.get_field(field)

                if new_field:
                    fields.append(new_field)
                    self._info('added\t{0}{1}/models.py\t{2} field'.format(
                        self.SCAFFOLD_APPS_DIR, self.app, field.split(':')[1]), 1)

        # Open models.py to append
        with open('{0}{1}/models.py'.format(self.SCAFFOLD_APPS_DIR, self.app), 'a') as fp:
            fp.write(''.join([import_line for import_line in self.imports]))
            fp.write(MODEL_TEMPLATE % (self.model, ''.join(field for field in fields)))

    def create_templates(self):
        self._info(" Templates ")
        self._info("===========")

        # Check if template dir exists

        if path.exists('{0}{1}/templates/'.format(self.SCAFFOLD_APPS_DIR, self.app)):
            self._info('exists\t{0}{1}/templates/'.format(self.SCAFFOLD_APPS_DIR, self.app), 1)
        else:
            mkdir("{0}{1}/templates/".format(self.SCAFFOLD_APPS_DIR, self.app))
            self._info('create\t{0}{1}/templates/'.format(self.SCAFFOLD_APPS_DIR, self.app), 1)

        # Check if model template dir exists

        if path.exists('{0}{1}/templates/{2}/'.format(self.SCAFFOLD_APPS_DIR, self.app,
                                                      self.model.lower())):
            self._info('exists\t{0}{1}/templates/{2}/'.format(self.SCAFFOLD_APPS_DIR, self.app,
                                                              self.model.lower()), 1)
        else:
            mkdir("{0}{1}/templates/{2}/".format(self.SCAFFOLD_APPS_DIR, self.app,
                                                 self.model.lower()))
            self._info('create\t{0}{1}/templates/{2}/'.format(
                self.SCAFFOLD_APPS_DIR, self.app, self.model.lower()), 1)

        # Check if list.html exists

        if path.exists('{0}{1}/templates/{2}/list.html'.format(self.SCAFFOLD_APPS_DIR, self.app,
                                                               self.model.lower())):
            self._info('exists\t{0}{1}/templates/{2}/list.html'.format(
                self.SCAFFOLD_APPS_DIR, self.app, self.model.lower()), 1)
        else:
            with open("{0}{1}/templates/{2}/list.html".format(self.SCAFFOLD_APPS_DIR, self.app,
                                                              self.model.lower()), 'w') as fp:
                fp.write(TEMPLATE_LIST_CONTENT % {
                    'model': self.model.lower(),
                    'title': self.model.lower(),
                })
            self._info('create\t{0}{1}/templates/{2}/list.html'.format(
                self.SCAFFOLD_APPS_DIR, self.app, self.model.lower()), 1)

        # Check if details.html exists

        if path.exists('{0}{1}/templates/{2}/details.html'.format(
                self.SCAFFOLD_APPS_DIR, self.app, self.model.lower())):
            self._info('exists\t{0}{1}/templates/{2}/details.html'.format(
                self.SCAFFOLD_APPS_DIR, self.app, self.model.lower()), 1)
        else:
            with open("{0}{1}/templates/{2}/details.html".format(
                    self.SCAFFOLD_APPS_DIR, self.app, self.model.lower()), 'w') as fp:
                fp.write(TEMPLATE_DETAILS_CONTENT % {
                    'model': self.model.lower(),
                    'title': self.model.lower(),
                })
            self._info('create\t{0}{1}/templates/{2}/details.html'.format(
                self.SCAFFOLD_APPS_DIR, self.app, self.model.lower()), 1)

    def create_urls(self):
        self._info("    URLs   ")
        self._info("===========")

        # Check if urls.py exists

        if path.exists('{0}{1}/urls.py'.format(self.SCAFFOLD_APPS_DIR, self.app)):

            # If does we need to add urls
            new_urls = ''
            with open("{0}{1}/urls.py".format(self.SCAFFOLD_APPS_DIR, self.app), 'r') as fp:
                for line in fp.readlines():
                    new_urls += line
                    if 'urlpatterns' in line:
                        new_urls += URL_EXISTS_CONTENT % {
                            'app': self.app,
                            'model': self.model.lower(),
                        }
            with open("{0}{1}/urls.py".format(self.SCAFFOLD_APPS_DIR, self.app), 'w') as fp:
                fp.write(new_urls)
            self._info('update\t{0}{1}/urls.py'.format(self.SCAFFOLD_APPS_DIR, self.app), 1)
        else:
            with open("{0}{1}/urls.py".format(self.SCAFFOLD_APPS_DIR, self.app), 'w') as fp:
                fp.write(URL_CONTENT % {
                    'app': self.app,
                    'model': self.model.lower(),
                })

            self._info('create\t{0}{1}/urls.py'.format(self.SCAFFOLD_APPS_DIR, self.app), 1)

    def create_admin(self):
        self._info("    Admin  ")
        self._info("===========")

        # Check if admin.py exists

        if path.exists('{0}{1}/admin.py'.format(self.SCAFFOLD_APPS_DIR, self.app)):
            self._info('exists\t{0}{1}/admin.py'.format(self.SCAFFOLD_APPS_DIR, self.app), 1)
        else:
            with open("{0}{1}/admin.py".format(self.SCAFFOLD_APPS_DIR, self.app), 'w') as fp:
                fp.write("from django.contrib import admin\n")
            self._info('create\t{0}{1}/urls.py'.format(self.SCAFFOLD_APPS_DIR, self.app), 1)

        # Check if admin entry already exists

        with open("{0}{1}/admin.py".format(self.SCAFFOLD_APPS_DIR, self.app), 'r') as fp:
            content = fp.read()
        if "admin.site.register({0})".format(self.model) in content:
            self._info('exists\t{0}{1}/admin.py\t{2}'.format(self.SCAFFOLD_APPS_DIR, self.app,
                                                             self.model.lower()), 1)
        else:
            with open("{0}{1}/admin.py".format(self.SCAFFOLD_APPS_DIR, self.app), 'a') as fp:
                fp.write(ADMIN_CONTENT % {'app': self.app, 'model': self.model})
            self._info('added\t{0}{1}/admin.py\t{2}'.format(self.SCAFFOLD_APPS_DIR, self.app,
                                                            self.model.lower()), 1)

    def create_forms(self):
        self._info("    Forms  ")
        self._info("===========")

        # Check if forms.py exists
        if path.exists('{0}{1}/forms.py'.format(self.SCAFFOLD_APPS_DIR, self.app)):
            self._info('exists\t{0}{1}/forms.py'.format(self.SCAFFOLD_APPS_DIR, self.app), 1)
        else:
            with open("{0}{1}/forms.py".format(self.SCAFFOLD_APPS_DIR, self.app), 'w') as fp:
                fp.write("from django import forms\n")
            self._info('create\t{0}{1}/forms.py'.format(self.SCAFFOLD_APPS_DIR, self.app), 1)

        # Check if form entry already exists

        with open("{0}{1}/forms.py".format(self.SCAFFOLD_APPS_DIR, self.app), 'r') as fp:
            content = fp.read()
        if "class {0}Form".format(self.model) in content:
            self._info('exists\t{0}{1}/forms.py\t{2}'.format(
                self.SCAFFOLD_APPS_DIR, self.app, self.model.lower()), 1)
        else:
            with open("{0}{1}/forms.py".format(self.SCAFFOLD_APPS_DIR, self.app), 'a') as fp:
                fp.write(FORM_CONTENT % {'app': self.app, 'model': self.model})
            self._info('added\t{0}{1}/forms.py\t{2}'.format(
                self.SCAFFOLD_APPS_DIR, self.app, self.model.lower()), 1)

    def create_tests(self):
        self._info("   Tests   ")
        self._info("===========")

        # Check if tests.py exists
        if path.exists('{0}{1}/tests.py'.format(self.SCAFFOLD_APPS_DIR, self.app)):
            self._info('exists\t{0}{1}/tests.py'.format(self.SCAFFOLD_APPS_DIR, self.app), 1)
            # Check if imports exists:
            import_testcase = True
            import_user = True
            import_reverse = True

            with open("{0}{1}/tests.py".format(self.SCAFFOLD_APPS_DIR, self.app), 'r') as fp:
                for line in fp.readlines():
                    if 'import TestCase' in line:
                        import_testcase = False
                    if 'import User' in line:
                        import_user = False
                    if 'import reverse' in line:
                        import_reverse = False

            with open("{0}{1}/tests.py".format(self.SCAFFOLD_APPS_DIR, self.app), 'a') as fp:
                if import_testcase:
                    fp.write("from django.test import TestCase\n")
                if import_user:
                    fp.write("from django.contrib.auth.models import User\n")
                if import_reverse:
                    fp.write("from django.core.urlresolvers import reverse\n")
        else:
            with open("{0}{1}/tests.py".format(self.SCAFFOLD_APPS_DIR, self.app), 'w') as fp:
                fp.write("from django.test import TestCase\n")
                fp.write("from django.contrib.auth.models import User\n")
                fp.write("from django.core.urlresolvers import reverse\n")
            self._info('create\t{0}{1}/tests.py'.format(self.SCAFFOLD_APPS_DIR, self.app), 1)

        # Check if test class already exists
        with open("{0}{1}/tests.py".format(self.SCAFFOLD_APPS_DIR, self.app), 'r') as fp:
            content = fp.read()
        if "class {0}Test".format(self.model) in content:
            self._info('exists\t{0}{1}/tests.py\t{2}'.format(
                self.SCAFFOLD_APPS_DIR, self.app, self.model.lower()), 1)
        else:
            with open("{0}{1}/tests.py".format(self.SCAFFOLD_APPS_DIR, self.app), 'a') as fp:
                fp.write(TESTS_CONTENT % {
                    'app': self.app,
                    'model': self.model,
                    'lower_model': self.model.lower(),
                })

            self._info('added\t{0}{1}/tests.py\t{2}'.format(self.SCAFFOLD_APPS_DIR, self.app,
                                                            self.model.lower()), 1)

    def run(self):
        if not self.app:
            sys.exit("No application name found...")
        if not self.app.isalnum():
            sys.exit("Model name should be alphanumerical...")
        self.create_app()
        if self.model:
            self.create_model()
            self.create_views()
            self.create_admin()
            self.create_forms()
            self.create_urls()
            self.create_templates()
            self.create_tests()
