from __future__ import print_function, unicode_literals, with_statement, division

from django.db import models
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.admin.options import BaseModelAdmin, ModelAdmin
from django.contrib.admin.helpers import AdminForm
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.translation import ugettext as _
from django.utils.html import escape
from django.forms.formsets import all_valid
from django.contrib.admin import helpers
from django.utils.safestring import mark_safe
from django.forms.models import (inlineformset_factory, BaseInlineFormSet)
from django import forms
from django.utils.functional import curry

from django_common.compat import (atomic_decorator, force_unicode,
                                  unquote, flatten_fieldsets)


csrf_protect_m = method_decorator(csrf_protect)


def __init__(self, form, fieldsets, prepopulated_fields, readonly_fields=None, model_admin=None):
    """
    Monkey-patch for django 1.5
    """
    def normalize_fieldsets(fieldsets):
        """
        Make sure the keys in fieldset dictionaries are strings. Returns the
        normalized data.
        """
        result = []

        for name, options in fieldsets:
            result.append((name, normalize_dictionary(options)))

        return result

    def normalize_dictionary(data_dict):
        """
        Converts all the keys in "data_dict" to strings. The keys must be
        convertible using str().
        """
        for key, value in data_dict.items():
            if not isinstance(key, str):
                del data_dict[key]
                data_dict[str(key)] = value

        return data_dict

    if isinstance(prepopulated_fields, list):
        prepopulated_fields = dict()

    self.form, self.fieldsets = form, normalize_fieldsets(fieldsets)
    self.prepopulated_fields = [{
        'field': form[field_name],
        'dependencies': [form[f] for f in dependencies]
    } for field_name, dependencies in prepopulated_fields.items()]

    self.model_admin = model_admin

    if readonly_fields is None:
        readonly_fields = ()

    self.readonly_fields = readonly_fields

AdminForm.__init__ = __init__


class NestedModelAdmin(ModelAdmin):

    @csrf_protect_m
    @atomic_decorator
    def add_view(self, request, form_url='', extra_context=None):
        """The 'add' admin view for this model."""
        model = self.model
        opts = model._meta

        if not self.has_add_permission(request):
            raise PermissionDenied

        ModelForm = self.get_form(request)
        formsets = []

        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES)

            if form.is_valid():
                new_object = self.save_form(request, form, change=False)
                form_validated = True
            else:
                form_validated = False
                new_object = self.model()

            prefixes = {}

            for FormSet, inline in zip(self.get_formsets(request),
                                       self.get_inline_instances(request)):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1

                if prefixes[prefix] != 1:
                    prefix = "{0}-{1}".format(prefix, prefixes[prefix])

                formset = FormSet(data=request.POST, files=request.FILES,
                                  instance=new_object,
                                  save_as_new="_saveasnew" in request.POST,
                                  prefix=prefix, queryset=inline.queryset(request))

                formsets.append(formset)

                for inline in self.get_inline_instances(request):
                    # If this is the inline that matches this formset, and
                    # we have some nested inlines to deal with, then we need
                    # to get the relevant formset for each of the forms in
                    # the current formset.
                    if inline.inlines and inline.model == formset.model:
                        for nested in inline.inline_instances:
                            for the_form in formset.forms:
                                InlineFormSet = nested.get_formset(request, the_form.instance)
                                prefix = "{0}-{1}".format(the_form.prefix,
                                                          InlineFormSet.get_default_prefix())
                                formsets.append(InlineFormSet(request.POST, request.FILES,
                                                              instance=the_form.instance,
                                                              prefix=prefix))
            if all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, change=False)
                form.save_m2m()

                for formset in formsets:
                    self.save_formset(request, form, formset, change=False)

                self.log_addition(request, new_object)

                return self.response_add(request, new_object)
        else:
            # Prepare the dict of initial data from the request.
            # We have to special-case M2Ms as a list of comma-separated PKs.
            initial = dict(request.GET.items())

            for k in initial:
                try:
                    f = opts.get_field(k)
                except models.FieldDoesNotExist:
                    continue

                if isinstance(f, models.ManyToManyField):
                    initial[k] = initial[k].split(",")

            form = ModelForm(initial=initial)
            prefixes = {}

            for FormSet, inline in zip(self.get_formsets(request),
                                       self.get_inline_instances(request)):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1

                if prefixes[prefix] != 1:
                    prefix = "{0}-{1}".format(prefix, prefixes[prefix])

                formset = FormSet(instance=self.model(), prefix=prefix,
                                  queryset=inline.queryset(request))
                formsets.append(formset)

        adminForm = helpers.AdminForm(form, list(self.get_fieldsets(request)),
                                      self.prepopulated_fields, self.get_readonly_fields(request),
                                      model_admin=self)

        media = self.media + adminForm.media
        inline_admin_formsets = []

        for inline, formset in zip(self.get_inline_instances(request), formsets):
            fieldsets = list(inline.get_fieldsets(request))
            readonly = list(inline.get_readonly_fields(request))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset,
                                                              fieldsets, readonly,
                                                              model_admin=self)
            if inline.inlines:
                for form in formset.forms:
                    if form.instance.pk:
                        instance = form.instance
                    else:
                        instance = None

                    form.inlines = inline.get_inlines(request, instance, prefix=form.prefix)

                inline_admin_formset.inlines = inline.get_inlines(request)

            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        context = {
            'title': _('Add %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'is_popup': "_popup" in request.REQUEST,
            'show_delete': False,
            'media': mark_safe(media),
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'app_label': opts.app_label,
        }

        context.update(extra_context or {})

        return self.render_change_form(request, context, form_url=form_url, add=True)

    @csrf_protect_m
    @atomic_decorator
    def change_view(self, request, object_id, extra_context=None, **kwargs):
        "The 'change' admin view for this model."
        model = self.model
        opts = model._meta
        obj = self.get_object(request, unquote(object_id))

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') %
                          {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        if request.method == 'POST' and "_saveasnew" in request.POST:
            return self.add_view(request, form_url='../add/')

        ModelForm = self.get_form(request, obj)
        formsets = []

        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES, instance=obj)

            if form.is_valid():
                form_validated = True
                new_object = self.save_form(request, form, change=True)
            else:
                form_validated = False
                new_object = obj

            prefixes = {}

            for FormSet, inline in zip(self.get_formsets(request, new_object),
                                       self.get_inline_instances(request)):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1

                if prefixes[prefix] != 1:
                    prefix = "{0}-{1}".format(prefix, prefixes[prefix])
                formset = FormSet(request.POST, request.FILES,
                                  instance=new_object, prefix=prefix,
                                  queryset=inline.queryset(request))

                formsets.append(formset)

                for inline in self.get_inline_instances(request):
                    # If this is the inline that matches this formset, and
                    # we have some nested inlines to deal with, then we need
                    # to get the relevant formset for each of the forms in
                    # the current formset.
                    if inline.inlines and inline.model == formset.model:
                        for nested in inline.inline_instances:
                            for the_form in formset.forms:
                                InlineFormSet = nested.get_formset(request, the_form.instance)
                                prefix = "{0}-{1}".format(the_form.prefix,
                                                          InlineFormSet.get_default_prefix())
                                formsets.append(InlineFormSet(request.POST, request.FILES,
                                                              instance=the_form.instance,
                                                              prefix=prefix))
            if all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, change=True)
                form.save_m2m()

                for formset in formsets:
                    self.save_formset(request, form, formset, change=True)

                change_message = self.construct_change_message(request, form, formsets)
                self.log_change(request, new_object, change_message)

                return self.response_change(request, new_object)

        else:
            form = ModelForm(instance=obj)
            prefixes = {}

            for FormSet, inline in zip(self.get_formsets(request, obj),
                                       self.get_inline_instances(request)):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "{0}-{1}".format(prefix, prefixes[prefix])
                formset = FormSet(instance=obj, prefix=prefix,
                                  queryset=inline.queryset(request))
                formsets.append(formset)

        adminForm = helpers.AdminForm(form, self.get_fieldsets(request, obj),
                                      self.prepopulated_fields,
                                      self.get_readonly_fields(request, obj),
                                      model_admin=self)
        media = self.media + adminForm.media
        inline_admin_formsets = []

        for inline, formset in zip(self.get_inline_instances(request), formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            readonly = list(inline.get_readonly_fields(request, obj))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset, fieldsets,
                                                              readonly, model_admin=self)
            if inline.inlines:
                for form in formset.forms:
                    if form.instance.pk:
                        instance = form.instance
                    else:
                        instance = None

                    form.inlines = inline.get_inlines(request, instance, prefix=form.prefix)

                inline_admin_formset.inlines = inline.get_inlines(request)

            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        context = {
            'title': _('Change %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'object_id': object_id,
            'original': obj,
            'is_popup': "_popup" in request.REQUEST,
            'media': mark_safe(media),
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'app_label': opts.app_label,
        }

        context.update(extra_context or {})

        return self.render_change_form(request, context, change=True, obj=obj)

    def get_inlines(self, request, obj=None, prefix=None):
        nested_inlines = []

        for inline in self.get_inline_instances(request):
            FormSet = inline.get_formset(request, obj)
            prefix = "{0}-{1}".format(prefix, FormSet.get_default_prefix())
            formset = FormSet(instance=obj, prefix=prefix)
            fieldsets = list(inline.get_fieldsets(request, obj))
            nested_inline = helpers.InlineAdminFormSet(inline, formset, fieldsets)
            nested_inlines.append(nested_inline)

        return nested_inlines


class NestedTabularInline(BaseModelAdmin):
    """
    Options for inline editing of ``model`` instances.

    Provide ``name`` to specify the attribute name of the ``ForeignKey`` from
    ``model`` to its parent. This is required if ``model`` has more than one
    ``ForeignKey`` to its parent.
    """
    model = None
    fk_name = None
    formset = BaseInlineFormSet
    extra = 3
    max_num = None
    template = None
    verbose_name = None
    verbose_name_plural = None
    can_delete = True
    template = 'common/admin/nested_tabular.html'
    inlines = []

    def __init__(self, parent_model, admin_site):
        self.admin_site = admin_site
        self.parent_model = parent_model
        self.opts = self.model._meta
        super(NestedTabularInline, self).__init__()

        if self.verbose_name is None:
            self.verbose_name = self.model._meta.verbose_name

        if self.verbose_name_plural is None:
            self.verbose_name_plural = self.model._meta.verbose_name_plural

        self.inline_instances = []

        for inline_class in self.inlines:
            inline_instance = inline_class(self.model, self.admin_site)
            self.inline_instances.append(inline_instance)

    def _media(self):
        from django.conf import settings

        js = ['js/jquery.min.js', 'js/jquery.init.js', 'js/inlines.min.js']

        if self.prepopulated_fields:
            js.append('js/urlify.js')
            js.append('js/prepopulate.min.js')

        if self.filter_vertical or self.filter_horizontal:
            js.extend(['js/SelectBox.js', 'js/SelectFilter2.js'])

        return forms.Media(js=['{0}{1}'.format(settings.ADMIN_MEDIA_PREFIX, url) for url in js])

    media = property(_media)

    def get_formset(self, request, obj=None, **kwargs):
        """
        Returns a BaseInlineFormSet class for use in admin add/change views.
        """
        if self.declared_fieldsets:
            fields = flatten_fieldsets(self.declared_fieldsets)
        else:
            fields = None
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)

        exclude.extend(kwargs.get("exclude", []))
        exclude.extend(self.get_readonly_fields(request, obj))

        # if exclude is an empty list we use None, since that's the actual
        # default
        exclude = exclude or None
        defaults = {
            "form": self.form,
            "formset": self.formset,
            "fk_name": self.fk_name,
            "fields": fields,
            "exclude": exclude,
            "formfield_callback": curry(self.formfield_for_dbfield, request=request),
            "extra": self.extra,
            "max_num": self.max_num,
            "can_delete": self.can_delete,
        }
        defaults.update(kwargs)

        return inlineformset_factory(self.parent_model, self.model, **defaults)

    def get_fieldsets(self, request, obj=None):
        if self.declared_fieldsets:
            return self.declared_fieldsets

        form = self.get_formset(request).form
        fields = form.base_fields.keys() + list(self.get_readonly_fields(request, obj))

        return [(None, {'fields': fields})]

    def get_inlines(self, request, obj=None, prefix=None):
        nested_inlines = []

        for inline in self.inline_instances:
            FormSet = inline.get_formset(request, obj)
            prefix = "{0}-{1}".format(prefix, FormSet.get_default_prefix())
            formset = FormSet(instance=obj, prefix=prefix)
            fieldsets = list(inline.get_fieldsets(request, obj))
            nested_inline = helpers.InlineAdminFormSet(inline, formset, fieldsets)
            nested_inlines.append(nested_inline)

        return nested_inlines
