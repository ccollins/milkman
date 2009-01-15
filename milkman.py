import random, string, datetime, itertools

from django.db.models.fields.related import RelatedField, ManyToManyField
from django.db import models

class MilkmanRegistry(object):
    """docstring for MilkmanRegistry"""
    def __init__(self):
        self.default_generators = {}
    
    def add_generator(self, cls, func):
        self.default_generators[cls] = func
    
    def get(self, cls):
        return self.default_generators.get(cls, lambda f: loop(lambda: ''))
registry = MilkmanRegistry()

class MilkTruck(object):
    def __init__(self, model_class):
        self.model_class = model_class
        self.generators = {}
    
    def deliver(self, the_milkman, **explicit_values):
        exclude = []
        if explicit_values:
            exclude = explicit_values.keys()
        
        target = self.model_class()
        
        self.set_explicit_values(target, explicit_values)
        self.set_local_fields(target, the_milkman, exclude)
        target.save()
        
        self.set_m2m_explicit_values(target, explicit_values)
        self.set_m2m_fields(target, the_milkman, exclude)
        
        return target

    def is_m2m(self, field):
        return field in [f.name for f in self.model_class._meta.local_many_to_many]
    

    def set_explicit_values(self, target, explicit_values):
        for k,v in explicit_values.iteritems():
            if not self.is_m2m(k):
                setattr(target, k, v)

    def set_m2m_explicit_values(self, target, explicit_values):
        for k,vs in explicit_values.iteritems():
            if self.is_m2m(k):
                setattr(target, k, vs)

    def set_local_fields(self, target, the_milkman, exclude):
        for field in self.fields_to_generate(self.model_class._meta.local_fields, exclude):
            if isinstance(field, RelatedField):
                v = the_milkman.deliver(field.rel.to)
            else:
                v = self.generator_for(field).next()
            setattr(target, field.name, v)

    def set_m2m_fields(self, target, the_milkman, exclude):
        for field in self.fields_to_generate(self.model_class._meta.local_many_to_many, exclude):
            setattr(target, field.name, [the_milkman.deliver(field.rel.to)])

    def generator_for(self, field):
        field_cls = type(field)
        if not self.generators.has_key(field.name):
            gen_maker = registry.get(field_cls)
            generator = gen_maker(field)
            self.generators[field.name] = generator()
        return self.generators[field.name]

    def fields_to_generate(self, l, exclude):
        return [f for f in l if f.name not in exclude and self.needs_generated_value(f)]
    
    def needs_generated_value(self, field):
        return not field.has_default() and not field.blank and not field.null    

class Milkman(object):
    def __init__(self):
        self.trucks = {}

    def deliver(self, model_class, **explicit_values):
        """
        Create a new instance of model class with all required fields populated
        with test data from appropriate generator functions.
        """
        truck = self.trucks.setdefault(model_class, MilkTruck(model_class))
        return truck.deliver(self, **explicit_values)
milkman = Milkman()

###
#  Test Data Generators
###

def loop(func):
    def loop_generator(*args, **kwargs):
        while 1: 
            yield func(*args, **kwargs)
    return loop_generator
        
def sequence(func):
    def sequence_generator(*args, **kwargs):
        i = 0
        while 1: 
            i += 1
            yield func(i, *args, **kwargs)
    return sequence_generator

def default_gen_maker(field):
    return loop(lambda: '')

def random_choice_iterator(choices=[''], size=1):
    for i in range(0, size):
        yield random.choice(choices)

DEFAULT_STRING_LENGTH = 8
def random_string_maker(field, chars=None):
    max_length = getattr(field, 'max_length', DEFAULT_STRING_LENGTH)
    return loop(lambda: random_string(max_length, chars))

def random_string(max_length=None, chars=None):
    if max_length is None:
        max_length = DEFAULT_STRING_LENGTH
    if chars is None:
        chars = (string.ascii_letters + string.digits)
    i = random_choice_iterator(chars, max_length)
    return ''.join(x for x in i)

def random_boolean(field=None):
    return loop(lambda: random.choice((True, False)))

def random_date_string():
    y = random.randint(1900, 2020)
    m = random.randint(1, 12)
    d = random.randint(1, 28)
    return str(datetime.date(y, m, d))

def random_date_string_maker(field):
    return loop(random_date_string)

def random_datetime_string():
    h = random.randint(1, 12)
    m = random.randint(0, 59)
    result = "%s %d:%d" % (random_date_string(), h, m)
    return result

def random_datetime_string_maker(field):
    return loop(random_datetime_string)

tmpl = "%%d.%%0%dd"
def random_decimal(field):
    x = pow(10, field.max_digits - field.decimal_places) - 1
    y = pow(10, field.decimal_places) - 1
    fmt_string = tmpl % field.decimal_places
    def gen():
        return fmt_string % (random.randint(1, x), random.randint(1, y))
    return loop(gen)
    
def email_generator(addr, domain):
    template = "%s%%d@%s" % (addr, domain)
    def email_gen_maker(field):
        return sequence(lambda i: template % i)
    return email_gen_maker

def random_integer(field):
    return loop(lambda: random.randint(1, 100))

registry.add_generator(models.BooleanField, random_boolean)
registry.add_generator(models.CharField, random_string_maker)
# registry.add_generator(models.CommaSeparatedIntegerField, default_generator)
registry.add_generator(models.DateField, random_date_string_maker)
registry.add_generator(models.DateTimeField, random_datetime_string_maker)
registry.add_generator(models.DecimalField, random_decimal)
registry.add_generator(models.EmailField, email_generator('user', 'example.com'))
# registry.add_generator(models.FileField, default_generator)
# registry.add_generator(models.FilePathField, default_generator)
# registry.add_generator(models.FloatField, default_generator)
# registry.add_generator(models.ImageField, default_generator)
registry.add_generator(models.IntegerField, random_integer)
# registry.add_generator(models.IPAddressField, default_generator)
# registry.add_generator(models.NullBooleanField, default_generator)
# registry.add_generator(models.PositiveIntegerField, default_generator)
# registry.add_generator(models.PositiveSmallIntegerField, default_generator)
# registry.add_generator(models.SlugField, default_generator)
# registry.add_generator(models.SmallIntegerField, default_generator)
# registry.add_generator(models.TextField, default_generator)
# registry.add_generator(models.TimeField, default_generator)
# registry.add_generator(models.URLField, default_generator)
# registry.add_generator(models.XMLField, default_generator)
