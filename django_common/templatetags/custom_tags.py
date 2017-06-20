from __future__ import print_function, unicode_literals, with_statement, division

from django import template
from django.forms import widgets
from django.template.loader import get_template

register = template.Library()


class FormFieldNode(template.Node):
    """
    Helper class for the render_form_field below
    """
    def __init__(self, form_field, help_text=None, css_classes=None):
        self.form_field = template.Variable(form_field)
        self.help_text = help_text[1:-1] if help_text else help_text
        self.css_classes = css_classes[1:-1] if css_classes else css_classes

    def render(self, context):

        try:
            form_field = self.form_field.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        widget = form_field.field.widget

        if isinstance(widget, widgets.HiddenInput):
            return form_field
        elif isinstance(widget, widgets.RadioSelect):
            t = get_template('common/fragments/radio_field.html')
        elif isinstance(widget, widgets.CheckboxInput):
            t = get_template('common/fragments/checkbox_field.html')
        elif isinstance(widget, widgets.CheckboxSelectMultiple):
            t = get_template('common/fragments/multi_checkbox_field.html')
        else:
            t = get_template('common/fragments/form_field.html')

        help_text = self.help_text
        if help_text is None:
            help_text = form_field.help_text

        return t.render({
            'form_field': form_field,
            'help_text': help_text,
            'css_classes': self.css_classes
        })


@register.tag
def render_form_field(parser, token):
    """
    Usage is {% render_form_field form.field_name optional_help_text optional_css_classes %}

    - optional_help_text and optional_css_classes are strings
    - if optional_help_text is not given, then it is taken from form field object
    """
    try:
        help_text = None
        css_classes = None

        token_split = token.split_contents()
        if len(token_split) == 4:
            tag_name, form_field, help_text, css_classes = token.split_contents()
        elif len(token_split) == 3:
            tag_name, form_field, help_text = token.split_contents()
        else:
            tag_name, form_field = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "Unable to parse arguments for {0}".format(repr(token.contents.split()[0])))

    return FormFieldNode(form_field, help_text=help_text, css_classes=css_classes)


@register.simple_tag
def active(request, pattern):
    """
    Returns the string 'active' if pattern matches.
    Used to assign a css class in navigation bars to active tab/section.
    """
    if request.path == pattern:
        return 'active'
    return ''


@register.simple_tag
def active_starts(request, pattern):
    """
    Returns the string 'active' if request url starts with pattern.
    Used to assign a css class in navigation bars to active tab/section.
    """
    if request.path.startswith(pattern):
        return 'active'
    return ''
