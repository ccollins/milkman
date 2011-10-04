from django.db import models
from django.db.models.fields.related import RelatedField

from milkman import generators


class MilkmanRegistry(object):
    default_generators = {}

    def __init__(self):
        try:
            self.add_generator(models.BigIntegerField,
                generators.random_big_integer_maker)
        except AttributeError:
            pass  # Only supported in django 1.2+

        self.add_generator(models.AutoField,
            generators.random_auto_field_maker)
        self.add_generator(models.BooleanField,
            generators.random_boolean_maker)
        self.add_generator(models.CharField,
            generators.random_string_maker)
        self.add_generator(models.CommaSeparatedIntegerField,
            generators.random_comma_seperated_integer_maker)
        self.add_generator(models.DateField,
            generators.random_date_string_maker)
        self.add_generator(models.DateTimeField,
            generators.random_datetime_string_maker)
        self.add_generator(models.DecimalField,
            generators.random_decimal_maker)
        self.add_generator(models.EmailField,
            generators.email_generator('user', 'example.com'))
        self.add_generator(models.FloatField,
            generators.random_float_maker)
        self.add_generator(models.IntegerField,
            generators.random_integer_maker)
        self.add_generator(models.IPAddressField,
            generators.random_ipaddress_maker)
        self.add_generator(models.NullBooleanField,
            generators.random_null_boolean_maker)
        self.add_generator(models.PositiveIntegerField,
            generators.random_positive_integer_maker)
        self.add_generator(models.PositiveSmallIntegerField,
            generators.random_small_positive_integer_maker)
        self.add_generator(models.SlugField,
            generators.random_string_maker)
        self.add_generator(models.SmallIntegerField,
            generators.random_small_integer_maker)
        self.add_generator(models.TextField,
            generators.random_string_maker)
        self.add_generator(models.TimeField,
            generators.random_time_string_maker)
        # self.add_generator(models.URLField, generators.random_url_maker)
        # self.add_generator(models.FileField, default_generator)
        # self.add_generator(models.FilePathField, default_generator)
        # self.add_generator(models.ImageField, default_generator)
        # self.add_generator(models.XMLField, default_generator)

    def add_generator(self, cls, func):
        self.default_generators[cls] = func

    def get(self, cls):
        return self.default_generators.get(cls,
            lambda f: generators.loop(lambda: ''))


class MilkTruck(object):
    generators = {}

    def __init__(self, model_class):
        if isinstance(model_class, basestring):
           model_class = self.get_model_class_from_string(model_class)
        self.model_class = model_class

    def get_model_class_from_string(self, model_name):
        assert '.' in model_name, ("'model_class' must be either a model"
                                   " or a model name in the format"
                                   " app_label.model_name")
        app_label, model_name = model_name.split(".")
        return models.get_model(app_label, model_name)

    def deliver(self, the_milkman, **explicit_values):

        model_explicit_values = {}
        related_explicit_values = {}
        for key, value in explicit_values.iteritems():
            if '__' in key:
                prefix, sep, postfix = key.partition('__')
                related_explicit_values.setdefault(prefix, {})
                related_explicit_values[prefix][postfix] = value
            else:
                model_explicit_values[key] = value

        exclude = []
        if model_explicit_values:
            exclude = model_explicit_values.keys()

        target = self.model_class()

        self.set_explicit_values(target, model_explicit_values)
        self.set_local_fields(target, the_milkman, exclude, related_explicit_values)
        target.save()

        self.set_m2m_explicit_values(target, model_explicit_values)
        self.set_m2m_fields(target, the_milkman, exclude, related_explicit_values)

        return target

    def is_m2m(self, field):
        return field in [f.name for f in
            self.model_class._meta.local_many_to_many]

    def has_explicit_through_table(self, field):
        if isinstance(field.rel.through, models.base.ModelBase):  # Django 1.2
            return not field.rel.through._meta.auto_created
        if isinstance(field.rel.through, (str, unicode)):  # Django 1.1
            return True
        return False

    def set_explicit_values(self, target, explicit_values):
        for k, v in explicit_values.iteritems():
            if not self.is_m2m(k):
                setattr(target, k, v)

    def set_m2m_explicit_values(self, target, explicit_values):
        for k, vs in explicit_values.iteritems():
            if self.is_m2m(k):
                setattr(target, k, vs)

    def set_local_fields(self, target, the_milkman, exclude, related_explicit_values):
        for field in self.fields_to_generate(self.model_class._meta.fields,
                                             exclude):
            if isinstance(field, RelatedField):
                explicit_values = related_explicit_values.get(field.name, {})
                v = the_milkman.deliver(field.rel.to, **explicit_values)
            else:
                v = self.generator_for(the_milkman.registry, field).next()
            setattr(target, field.name, v)

    def set_m2m_fields(self, target, the_milkman, exclude, related_explicit_values):
        for field in self.fields_to_generate(
                self.model_class._meta.local_many_to_many, exclude):
            if not self.has_explicit_through_table(field):
                exclude = {}
                # if the target field is the same class, we don't want to keep
                # generating
                if type(target) == field.related.model:
                    exclude = {field.name: ''}
                explicit_values = related_explicit_values.get(field.name, {})
                explicit_values.update(exclude)
                setattr(target, field.name, [the_milkman.deliver(
                    field.rel.to, **explicit_values)])

    def generator_for(self, registry, field):
        field_cls = type(field)
        if not field.name in self.generators:
            gen_maker = registry.get(field_cls)
            generator = gen_maker(field)
            self.generators[field.name] = generator()
        return self.generators[field.name]

    def fields_to_generate(self, l, exclude):
        return [f for f in l if f.name not in exclude and
                self.needs_generated_value(f)]

    def needs_generated_value(self, field):
        return not field.has_default() and not field.blank and not field.null


class Milkman(object):
    def __init__(self, registry):
        self.trucks = {}
        self.registry = registry

    def deliver(self, model_class, **explicit_values):
        truck = self.trucks.setdefault(model_class, MilkTruck(model_class))
        return truck.deliver(self, **explicit_values)

milkman = Milkman(MilkmanRegistry())
