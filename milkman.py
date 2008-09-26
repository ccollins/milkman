import random
import string

from django.db.models.fields.related import RelatedField, ManyToManyField

_generators = {}

def gen(choices=[''], size=1):
    for i in range(0, size):
        yield random.choice(choices)

def add_generator(cls, func):
    global _generators
    _generators[cls] = func

def needs_generated_value(field):
    return not field.has_default() and not field.blank

def value_for(field):
    return _generators.get(type(field), lambda f: '')(field)

def random_string(field=None, chars=None):
    max_length = getattr(field, 'max_length', 8)
    if chars is None:
        chars = (string.ascii_letters + string.digits)
    return ''.join(x for x in gen(chars, max_length))

def deliver(model_class):
    result = model_class()
    options = model_class._meta
    _create_related(result, options.local_fields)
    result.save() # just in case
    _create_related(result, options.local_many_to_many, m2m=True)
    return result

def _create_related(parent, fields, m2m=False):
    related = [f for f in fields if is_deliverable(f)]
    if len(related):
        for f in related:
            obj = deliver(f.rel.to)
            if m2m: obj = [obj]
            setattr(parent, f.name, obj)
        parent.save()

def is_deliverable(f):
    # print f.name, f.__class__.__name__, f.blank, f.null
    return isinstance(f, RelatedField) and not f.blank and not f.null
    
def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()