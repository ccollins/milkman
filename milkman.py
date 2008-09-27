import random
import string

from django.db.models.fields.related import RelatedField, ManyToManyField
from django.db import models

DEFAULT_STRING_LENGTH = 8

_generators = {}

def gen(choices=[''], size=1):
    for i in range(0, size):
        yield random.choice(choices)

def add_generator(cls, func):
    global _generators
    _generators[cls] = func

def value_for(field):
    return _generators.get(type(field), lambda f: '')(field)

def random_string(field=None, chars=None):
    max_length = getattr(field, 'max_length', DEFAULT_STRING_LENGTH)
    if max_length is None:
        max_length = DEFAULT_STRING_LENGTH
    if chars is None:
        chars = (string.ascii_letters + string.digits)
    return ''.join(x for x in gen(chars, max_length))

def random_boolean(field=None):
    return random.choice((True, False))

add_generator(models.BooleanField, random_boolean)
add_generator(models.CharField, random_string)
# add_generator(models.CommaSeparatedIntegerField, default_generator)
# add_generator(models.DateField, default_generator)
# add_generator(models.DateTimeField, default_generator)
# add_generator(models.DecimalField, default_generator)
# add_generator(models.EmailField, default_generator)
# add_generator(models.FileField, default_generator)
# add_generator(models.FilePathField, default_generator)
# add_generator(models.FloatField, default_generator)
# add_generator(models.ImageField, default_generator)
# add_generator(models.IntegerField, default_generator)
# add_generator(models.IPAddressField, default_generator)
# add_generator(models.NullBooleanField, default_generator)
# add_generator(models.PositiveIntegerField, default_generator)
# add_generator(models.PositiveSmallIntegerField, default_generator)
# add_generator(models.SlugField, default_generator)
# add_generator(models.SmallIntegerField, default_generator)
# add_generator(models.TextField, default_generator)
# add_generator(models.TimeField, default_generator)
# add_generator(models.URLField, default_generator)
# add_generator(models.XMLField, default_generator)

def deliver(model_class):
    target = model_class()
    options = model_class._meta
    generate_local_fields(target, options)
    target.save()
    generate_m2m_fields(target, options)
    return target

def generate_local_fields(target, options):
    for f in gen_fields(options.local_fields):
        if isinstance(f, RelatedField):
            v = deliver(f.rel.to)
        else:
            v = value_for(f)
        setattr(target, f.name, v)

def generate_m2m_fields(target, options):
    for f in gen_fields(options.local_many_to_many):
        setattr(target, f.name, [deliver(f.rel.to)])

def gen_fields(l):
    return [f for f in l if needs_generated_value(f)]

def needs_generated_value(field):
    return not field.has_default() and not field.blank and not field.null


def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()