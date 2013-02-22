from django.db import models

class Root(models.Model):
    my_auto = models.AutoField(blank=False, null=False, primary_key=True)
    try:
        my_biginteger = models.BigIntegerField(blank=False, null=False)
    except AttributeError:
        pass
    my_boolean = models.BooleanField(blank=False, null=False)
    my_char = models.CharField(blank=False, null=False, max_length=16)
    my_commaseperatedinteger = models.CommaSeparatedIntegerField(blank=False, null=False, max_length=12)
    my_date = models.DateField(blank=False, null=False)
    my_datetime = models.DateTimeField(blank=False, null=False)
    my_decimal = models.DecimalField(blank=False, null=False, decimal_places=2, max_digits=4)
    my_email = models.EmailField(blank=False, null=False)
    # = models.FileField(blank=False, null=False)
    # = models.FilePathField(blank=False, null=False)
    my_float = models.FloatField(blank=False, null=False)
    # = models.ImageField(blank=False, null=False)
    my_integer = models.IntegerField(blank=False, null=False)
    my_ip = models.IPAddressField(blank=False, null=False)
    my_nullboolean = models.NullBooleanField(blank=False, null=False)
    my_positiveinteger = models.PositiveIntegerField(blank=False, null=False)
    my_positivesmallinteger = models.PositiveSmallIntegerField(blank=False, null=False)
    my_slug = models.SlugField(blank=False, null=False)
    my_smallinteger = models.SmallIntegerField(blank=False, null=False)
    my_text = models.TextField(blank=False, null=False)
    my_time = models.TimeField(blank=False, null=False)
    # = models.URLField(blank=False, null=False)
    # = models.XMLField(blank=False, null=False)

class Child(models.Model):
    name = models.CharField(blank=False, null=False, max_length=16)
    root = models.ForeignKey(Root, blank=False, null=False)

class Sibling(models.Model):
    name = models.CharField(blank=False, null=False, max_length=16)
    root = models.ForeignKey(Root, blank=True, null=True)

class GrandChild(models.Model):
    name = models.CharField(blank=False, null=False, max_length=16)
    parent = models.ForeignKey(Child)

class Uncle(models.Model):
    name = models.CharField(blank=False, null=False, max_length=16)

class Aunt(models.Model):
    name = models.CharField(blank=False, null=False, max_length=16)
    uncles = models.ManyToManyField(Uncle, blank=False, null=False)

class CounselingUncle(models.Model):
    uncle = models.ForeignKey(Uncle)
    cousin = models.ForeignKey("EstrangedChild")
    date_started = models.DateField()

class EstrangedChild(models.Model):
    name = models.CharField(max_length=16)
    uncles = models.ManyToManyField(Uncle, through=CounselingUncle)

class PsychoChild(models.Model):
    name = models.CharField(max_length=16)
    alter_egos = models.ManyToManyField("self")

class AdoptedChild(Child):
    birth_origin = models.CharField(max_length=100)

class ImageChild(Child):
    photo = models.ImageField(upload_to="uploads/")

class LongName(models.Model):
    name = models.CharField(max_length=200)

class ShortName(models.Model):
    name = models.CharField(max_length=100)

