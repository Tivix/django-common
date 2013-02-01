import binascii
import random
import string

from django.db.models import fields
from django.template.defaultfilters import slugify
from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson as json
from django import forms
from django.conf import settings


from south.modelsinspector import add_introspection_rules
from django_common.helper import md5_hash


class JSONField(models.TextField):
    """
    JSONField is a generic textfield that neatly serializes/unserializes JSON objects seamlessly
    """

    # Used so to_python() is called
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        """Convert our string value to JSON after we load it from the DB"""

        if value == "":
            return None

        try:
            if isinstance(value, basestring):
                return json.loads(value)
        except ValueError:
            pass

        return value

    def get_db_prep_save(self, value, connection=None):
        """Convert our JSON object to a string before we save"""

        if value == "":
            return None

        if isinstance(value, dict):
            value = json.dumps(value, cls=DjangoJSONEncoder)

        return super(JSONField, self).get_db_prep_save(value, connection)


class UniqueSlugField(fields.SlugField):
    """
    Represents a self-managing sluf field, that makes sure that the slug value is unique on the db table. Slugs by
    default get a db_index on them. The "Unique" in the class name is a misnomer since it does support unique=False

    @requires "prepopulate_from" in the constructor. This could be a field or a function in the model class which is using
    this field

    Defaults update_on_save to False

    Taken and edited from: http://www.djangosnippets.org/snippets/728/
    """
    def __init__(self, prepopulate_from='id', *args, **kwargs):
        if kwargs.get('update_on_save'):
            self.__update_on_save = kwargs.pop('update_on_save')
        else:
            self.__update_on_save = False
        self.prepopulate_from = prepopulate_from
        super(UniqueSlugField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        prepopulate_field = getattr(model_instance, self.prepopulate_from)
        if callable(prepopulate_field):
            prepopulate_value = prepopulate_field()
        else:
            prepopulate_value = prepopulate_field

        # if object has an id, and not to update on save, then return existig model instance's slug value
        if getattr(model_instance, 'id') and not self.__update_on_save:
            return getattr(model_instance, self.name)

        # if this is a previously saved object, and current instance's slug is same as one being proposed
        if getattr(model_instance, 'id') and getattr(model_instance, self.name) == slugify(prepopulate_value):
            return getattr(model_instance, self.name)

        # if a unique slug is not required (not the default of course)
        if not self.unique:
            return self.__set_and_return(model_instance, self.name, slugify(prepopulate_value))

        return self.__unique_slug(model_instance.__class__, model_instance, self.name,
                                  prepopulate_value)

    def __unique_slug(self, model, model_instance, slug_field, slug_value):
        orig_slug = slug = slugify(slug_value)
        index = 1
        while True:
            try:
                model.objects.get(**{slug_field: slug})
                index += 1
                slug = orig_slug + '-' + str(index)
            except model.DoesNotExist:
                return self.__set_and_return(model_instance, slug_field, slug)

    def __set_and_return(self, model_instance, slug_field, slug):
        setattr(model_instance, slug_field, slug)
        return slug

add_introspection_rules([
    (
        [UniqueSlugField],  # Class(es) these apply to
        [],         # Positional arguments (not used)
        {           # Keyword argument
            "prepopulate_from": ["prepopulate_from", {"default": 'id'}],
        },
    ),
], ["^django_common\.db_fields\.UniqueSlugField"])


class RandomHashField(fields.CharField):
    """
    Store a random hash for a certain model field.

    @param update_on_save optional field whether to update this hash or not, everytime the model instance is saved
    """
    def __init__(self, update_on_save=False, hash_length=None, *args, **kwargs):
        #TODO: args & kwargs serve no purpose but to make django evolution to work
        self.update_on_save = update_on_save
        self.hash_length = hash_length
        super(fields.CharField, self).__init__(max_length=128, unique=True, blank=False, null=False, db_index=True, default=md5_hash(max_length=self.hash_length))

    def pre_save(self, model_instance, add):
        if not add and not self.update_on_save:
            return getattr(model_instance, self.name)

        random_hash = md5_hash(max_length=self.hash_length)
        setattr(model_instance, self.name, random_hash)
        return random_hash

add_introspection_rules([
    (
        [RandomHashField],  # Class(es) these apply to
        [],         # Positional arguments (not used)
        {           # Keyword argument
            "update_on_save": ["update_on_save", {"default": False}],
            "hash_length": ["hash_length", {"default": None}],
        },
    ),
], ["^django_common\.db_fields\.RandomHashField"])


class BaseEncryptedField(models.Field):
    '''This code is based on the djangosnippet #1095
    You can find the original at http://www.djangosnippets.org/snippets/1095/'''

    def __init__(self, *args, **kwargs):
        cipher = kwargs.pop('cipher', 'AES')
        imp = __import__('Crypto.Cipher', globals(), locals(), [cipher], -1)
        self.cipher = getattr(imp, cipher).new(settings.SECRET_KEY[:32])
        self.prefix = '$%s$' % cipher

        max_length = kwargs.get('max_length', 40)
        mod = max_length % self.cipher.block_size
        if mod > 0:
            max_length += self.cipher.block_size - mod
        kwargs['max_length'] = max_length * 2 + len(self.prefix)

        models.Field.__init__(self, *args, **kwargs)

    def _is_encrypted(self, value):
        return isinstance(value, basestring) and value.startswith(self.prefix)

    def _get_padding(self, value):
        mod = len(value) % self.cipher.block_size
        if mod > 0:
            return self.cipher.block_size - mod
        return 0

    def to_python(self, value):
        if self._is_encrypted(value):
            return self.cipher.decrypt(binascii.a2b_hex(value[len(self.prefix):])).split('\0')[0]
        return value

    def get_db_prep_value(self, value, connection=None, prepared=None):
        if value is not None and not self._is_encrypted(value):
            padding = self._get_padding(value)
            if padding > 0:
                value += "\0" + ''.join([random.choice(string.printable) for index in range(padding - 1)])
            value = self.prefix + binascii.b2a_hex(self.cipher.encrypt(value))
        return value


class EncryptedTextField(BaseEncryptedField):
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return 'TextField'

    def formfield(self, **kwargs):
        defaults = {'widget': forms.Textarea}
        defaults.update(kwargs)
        return super(EncryptedTextField, self).formfield(**defaults)

add_introspection_rules([
    (
        [EncryptedTextField], [], {},
    ),
], ["^django_common\.db_fields\.EncryptedTextField"])


class EncryptedCharField(BaseEncryptedField):
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return "CharField"

    def formfield(self, **kwargs):
        defaults = {'max_length': self.max_length}
        defaults.update(kwargs)
        return super(EncryptedCharField, self).formfield(**defaults)

add_introspection_rules([
    (
        [EncryptedCharField], [], {},
    ),
], ["^django_common\.db_fields\.EncryptedCharField"])
