from django.db import models
from milkman import Milkman, MilkmanRegistry
import generators
    
registry = MilkmanRegistry()
registry.add_generator(models.BooleanField, generators.random_boolean)
registry.add_generator(models.CharField, generators.random_string_maker)
registry.add_generator(models.DateField, generators.random_date_string_maker)
registry.add_generator(models.DateTimeField, generators.random_datetime_string_maker)
registry.add_generator(models.DecimalField, generators.random_decimal)
registry.add_generator(models.EmailField, generators.email_generator('user', 'example.com'))
registry.add_generator(models.FloatField, generators.random_float_maker)
registry.add_generator(models.IntegerField, generators.random_integer)

milkman = Milkman(registry)

# registry.add_generator(models.CommaSeparatedIntegerField, default_generator)
# registry.add_generator(models.FileField, default_generator)
# registry.add_generator(models.FilePathField, default_generator)
# registry.add_generator(models.ImageField, default_generator)
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
