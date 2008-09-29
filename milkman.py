import random, string, datetime

from django.db.models.fields.related import RelatedField, ManyToManyField
from django.db import models
        
class Milkman(object):
    def __init__(self):
        self.generators = {}
    
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
            return generator(field)

    def generator_for(self, field):
        return self.generators.get(type(field), lambda f: '')

    def fields_to_generate(self, l):
        return [f for f in l if self.needs_generated_value(f)]
    
    def needs_generated_value(self, field):
        return not field.has_default() and not field.blank and not field.null    
milkman = Milkman()

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
def random_string(field=None, chars=None):
    max_length = getattr(field, 'max_length', DEFAULT_STRING_LENGTH)
    if max_length is None:
        max_length = DEFAULT_STRING_LENGTH
    if chars is None:
        chars = (string.ascii_letters + string.digits)
    i = random_choice_iterator(chars, max_length)
    return ''.join(x for x in i)

def random_boolean(field=None):
    return random.choice((True, False))

def random_date_string(field):
    y = random.randint(1900, 2020)
    m = random.randint(1, 12)
    d = random.randint(1, 28)
    return str(datetime.date(y, m, d))

def random_datetime_string(field):
    h = random.randint(1, 12)
    m = random.randint(0, 59)
    result = "%s %d:%d" % (random_date_string(field), h, m)
    return result

tmpl = "%%d.%%0%dd"
def random_decimal(field):
    x = pow(10, field.max_digits - field.decimal_places) - 1
    y = pow(10, field.decimal_places) - 1
    fmt_string = tmpl % field.decimal_places
    return fmt_string % (random.randint(1, x), random.randint(1, y))

def email_generator(addr, domain):
    ref = Ref(0)
    template = "%s%%d@%s" % (addr, domain)
    def random_email(field):
        ref.value += 1
        return template % ref.value
    return random_email

milkman.add_generator(models.BooleanField, random_boolean)
milkman.add_generator(models.CharField, random_string)
# milkman.add_generator(models.CommaSeparatedIntegerField, default_generator)
milkman.add_generator(models.DateField, random_date_string)
milkman.add_generator(models.DateTimeField, random_datetime_string)
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
