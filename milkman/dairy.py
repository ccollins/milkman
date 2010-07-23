from django.db import models
from django.db.models.fields.related import RelatedField

from milkman import generators


class MilkmanRegistry(object):
    
    def __init__(self):
        self.default_generators = {}
    
    def add_generator(self, cls, func):
        self.default_generators[cls] = func
    
    def get(self, cls):
        return self.default_generators.get(cls, lambda f: generators.loop(lambda: ''))

    @staticmethod
    def get_default():
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
        return registry


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
                v = self.generator_for(the_milkman.registry, field).next()
            setattr(target, field.name, v)

    def set_m2m_fields(self, target, the_milkman, exclude):
        for field in self.fields_to_generate(self.model_class._meta.local_many_to_many, exclude):
            setattr(target, field.name, [the_milkman.deliver(field.rel.to)])

    def generator_for(self, registry, field):
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
    def __init__(self, registry):
        self.trucks = {}
        self.registry = registry

    def deliver(self, model_class, **explicit_values):
        """
        Create a new instance of model class with all required fields populated
        with test data from appropriate generator functions.
        """
        truck = self.trucks.setdefault(model_class, MilkTruck(model_class))
        return truck.deliver(self, **explicit_values)


milkman = Milkman(MilkmanRegistry.get_default())
