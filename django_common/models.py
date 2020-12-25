from django.db import models


@property
def __data__(self):
    # noinspection PyProtectedMember
    data = {field.name: getattr(self, field.name) for field in self.__class__._meta.get_fields()}
    return data


models.Model.__data__ = __data__
