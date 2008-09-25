import random
import string
try:
    from django.db.models.fields.related import RelatedField
except:
    pass

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

def random_charactor(choices=None):
    return random.choice(char_set or string.ascii_letters)

def random_string(field=None, chars=None):
    max_length = getattr(field, 'max_length', 8)
    if chars is None:
        chars = (string.ascii_letters + string.digits)
    return ''.join(x for x in gen(chars, max_length))

def deliver(model_class):    
    result = model_class()
    options = model_class._meta    
    for f in options.local_fields:
        if _should_deliver_field(f):
            setattr(result, f.name, deliver(f.rel.to))
    result.save()
    return result

def _should_deliver_field(f):
    return isinstance(f, RelatedField) and \
        not f.null and \
        not f.blank
    
def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()