from django.db import models


@property
def __data__(self):
    # noinspection PyProtectedMember
    fields = self.__class__._meta.get_fields()
    data = {
        field.name: getattr(self, field.name)
        for field in fields 
        if not isinstance(field, models.fields.reverse_related.ManyToOneRel)
    }
    return data


models.Model.__data__ = __data__
