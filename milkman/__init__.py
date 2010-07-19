from django.db import models

from milkman import generators
from milkman.milk import Milkman, MilkmanRegistry


registry = MilkmanRegistry()

registry.add_generator(models.BooleanField, generators.random_boolean)
registry.add_generator(models.CharField, generators.random_string_maker)
registry.add_generator(models.SlugField, generators.random_string_maker)
registry.add_generator(models.DateField, generators.random_date_string_maker)
registry.add_generator(models.DateTimeField, generators.random_datetime_string_maker)
registry.add_generator(models.DecimalField, generators.random_decimal)
registry.add_generator(models.EmailField, generators.email_generator('user', 'example.com'))
registry.add_generator(models.FloatField, generators.random_float_maker)
registry.add_generator(models.IntegerField, generators.random_integer)

milkman = Milkman(registry)

