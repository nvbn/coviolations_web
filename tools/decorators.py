from itertools import ifilter
from django.db import models


def extend(model, no_meta=False):
    """Extend exist model"""
    def decorator(cls):
        for (attr, val) in ifilter(
            lambda (attr, val): attr[0:2] != '__', cls.__dict__.items(),
        ):
            if issubclass(type(val), models.Field):
                model.add_to_class(attr, val)
            elif attr == 'Meta' and not no_meta:
                extend(model._meta)(val)
            else:
                setattr(model, attr, val)
        return None
    return decorator
