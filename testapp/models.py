from django.db import models

class Root(models.Model):
    name = models.CharField(blank=False, null=False,max_length=16)
    boolean = models.BooleanField(blank=False, null=False)
    # = models.CharField(blank=False, null=False)
    # = models.CommaSeparatedIntegerField(blank=False, null=False)
    # = models.DateField(blank=False, null=False)
    # = models.DateTimeField(blank=False, null=False)
    # = models.DecimalField(blank=False, null=False)
    # = models.EmailField(blank=False, null=False)
    # = models.FileField(blank=False, null=False)
    # = models.FilePathField(blank=False, null=False)
    # = models.FloatField(blank=False, null=False)
    # = models.ImageField(blank=False, null=False)
    # = models.IntegerField(blank=False, null=False)
    # = models.IPAddressField(blank=False, null=False)
    # = models.NullBooleanField(blank=False, null=False)
    # = models.PositiveIntegerField(blank=False, null=False)
    # = models.PositiveSmallIntegerField(blank=False, null=False)
    # = models.SlugField(blank=False, null=False)
    # = models.SmallIntegerField(blank=False, null=False)
    # = models.TextField(blank=False, null=False)
    # = models.TimeField(blank=False, null=False)
    # = models.URLField(blank=False, null=False)
    # = models.XMLField(blank=False, null=False)


class Child(models.Model):
    name = models.CharField(blank=False, null=False, max_length=16)
    root = models.ForeignKey(Root, blank=False)

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