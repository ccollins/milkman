from django.db import models

class Root(models.Model):
    name = models.CharField(blank=False, null=False,max_length=16)

class Child(models.Model):
    name = models.CharField(blank=False, null=False, max_length=16)
    root = models.ForeignKey(Root, blank=False)
    
class Sibling(models.Model):
    name = models.CharField(blank=False, null=False, max_length=16)
    root = models.ForeignKey(Root, blank=True, null=True)

class GrandChild(models.Model):
    name = models.CharField(blank=False, null=False, max_length=16)
    parent = models.ForeignKey(Child)
