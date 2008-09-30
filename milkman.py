import random, string, datetime

from django.db.models.fields.related import RelatedField, ManyToManyField
from django.db import models

def infinity_machine(func):
    def infinite_generator(*args, **kwargs):
        while 1: 
            yield func(*args, **kwargs)
    return infinite_generator
        
class Milkman(object):
    def __init__(self):
        self.generators = {}
        self.registry = {}
    
    def add_generator(self, cls, func):
        self.generators[cls] = func
    
    def deliver(self, model_class):
        """
        Create a new instance of model class with all required fields populated
        with test data from appropriate generator functions.
        """
        target = model_class()
        options = model_class._meta
        for f in self.fields_to_generate(options.local_fields):
            setattr(target, f.name, self.value_for(f))
        target.save()
        for f in self.fields_to_generate(options.local_many_to_many):
            setattr(target, f.name, [self.deliver(f.rel.to)])
        return target

    def value_for(self, field):
        if isinstance(field, RelatedField):
            return self.deliver(field.rel.to)
        else:
            generator = self.generator_for(field)
            return generator.next()

    def generator_for(self, field):
        field_cls = type(field)
        if not self.registry.has_key(field_cls):
            gen_maker = self.generators.get(field_cls, default_gen_maker)
            self.registry[field_cls] = gen_maker(field)()
        return self.registry.get(field_cls)

    def fields_to_generate(self, l):
        return [f for f in l if self.needs_generated_value(f)]
    
    def needs_generated_value(self, field):
        return not field.has_default() and not field.blank and not field.null    
milkman = Milkman()

def default_gen_maker(field):
    return infinity_machine(lambda: '')
###
#  Test Data Generators
###
class Ref(object):
    """
    To work around Python's statically nested scopes.  Allows for:
    def outer(initial_value):
        ref = Ref(initial_value)
        def inner(arg):
            ref.value += 1
            return arg + ref.value
        return inner
    """
    def __init__(self, value):
        self.value = value

def random_choice_iterator(choices=[''], size=1):
    for i in range(0, size):
        yield random.choice(choices)

DEFAULT_STRING_LENGTH = 8
def random_string_maker(field, chars=None):
    max_length = getattr(field, 'max_length', DEFAULT_STRING_LENGTH)
    return infinity_machine(lambda: random_string(max_length, chars))

def random_string(max_length=None, chars=None):
    if max_length is None:
        max_length = DEFAULT_STRING_LENGTH
    if chars is None:
        chars = (string.ascii_letters + string.digits)
    i = random_choice_iterator(chars, max_length)
    return ''.join(x for x in i)

def random_boolean(field=None):
    return infinity_machine(lambda: random.choice((True, False)))

def random_date_string():
    y = random.randint(1900, 2020)
    m = random.randint(1, 12)
    d = random.randint(1, 28)
    return str(datetime.date(y, m, d))

def random_date_string_maker(field):
    return infinity_machine(random_date_string)

def random_datetime_string():
    h = random.randint(1, 12)
    m = random.randint(0, 59)
    result = "%s %d:%d" % (random_date_string(), h, m)
    return result

def random_datetime_string_maker(field):
    return infinity_machine(random_datetime_string)

tmpl = "%%d.%%0%dd"
def random_decimal(field):
    x = pow(10, field.max_digits - field.decimal_places) - 1
    y = pow(10, field.decimal_places) - 1
    fmt_string = tmpl % field.decimal_places
    def gen():
        return fmt_string % (random.randint(1, x), random.randint(1, y))
    return infinity_machine(gen)
    
def email_generator(addr, domain):
    ref = Ref(0)
    template = "%s%%d@%s" % (addr, domain)
    def maker(field):
        def random_email():
            ref.value += 1
            return template % ref.value
        return infinity_machine(random_email)
    return maker

milkman.add_generator(models.BooleanField, random_boolean)
milkman.add_generator(models.CharField, random_string_maker)
# milkman.add_generator(models.CommaSeparatedIntegerField, default_generator)
milkman.add_generator(models.DateField, random_date_string_maker)
milkman.add_generator(models.DateTimeField, random_datetime_string_maker)
milkman.add_generator(models.DecimalField, random_decimal)
milkman.add_generator(models.EmailField, email_generator('user', 'example.com'))
# milkman.add_generator(models.FileField, default_generator)
# milkman.add_generator(models.FilePathField, default_generator)
# milkman.add_generator(models.FloatField, default_generator)
# milkman.add_generator(models.ImageField, default_generator)
# milkman.add_generator(models.IntegerField, default_generator)
# milkman.add_generator(models.IPAddressField, default_generator)
# milkman.add_generator(models.NullBooleanField, default_generator)
# milkman.add_generator(models.PositiveIntegerField, default_generator)
# milkman.add_generator(models.PositiveSmallIntegerField, default_generator)
# milkman.add_generator(models.SlugField, default_generator)
# milkman.add_generator(models.SmallIntegerField, default_generator)
# milkman.add_generator(models.TextField, default_generator)
# milkman.add_generator(models.TimeField, default_generator)
# milkman.add_generator(models.URLField, default_generator)
# milkman.add_generator(models.XMLField, default_generator)
