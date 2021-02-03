from django.db import models


def check_may_to_many_field(field):
    return "m2m_reverse_target_field_name" in dir(field)


@property
def __data__(self):
    # noinspection PyProtectedMember
    fields = self.__class__._meta.get_fields()
    data = {
        field.name: getattr(self, field.name)
        for field in fields
        if not isinstance(field, models.fields.reverse_related.ManyToOneRel)
        and not check_may_to_many_field(field)
    }
    return data


models.Model.__data__ = __data__
