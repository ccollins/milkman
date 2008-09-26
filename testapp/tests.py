import unittest
import milkman
from testapp.models import Root, Child, Sibling, GrandChild, Aunt, Uncle
from django.db import models

MODELS = [Root, Child]
class ModelTest(unittest.TestCase):
    def tearDown(self):
        for m in MODELS:
            m._default_manager.all().delete()
    
    def test_create(self):
        r = milkman.deliver(Root)
        self.assertEqual(Root, r.__class__)
        self.assertTrue(bool(r.id))
        self.assert_(r.name is not None)

    def test_create_child(self):
        child = milkman.deliver(Child)
        self.assert_(child.root)
    
    def test_optional_relation(self):
        sibling = milkman.deliver(Sibling)
        self.assertEqual(None, sibling.root)
    
    def test_recurs_on_grandchildren(self):
        gc = milkman.deliver(GrandChild)
        self.assertNotEqual(None, gc.parent.root)

    def test_m2m(self):
        aunt = milkman.deliver(Aunt)
        self.assertEquals(1, len(aunt.uncles.all()))
        self.assertEquals(1, len(Uncle.objects.all()))
        self.assertEquals(Uncle.objects.all()[0], aunt.uncles.all()[0])

class FieldTest(unittest.TestCase):
    def test_needs_generated_value(self):
        f = Root._meta.get_field('name')
        assert milkman.needs_generated_value(f)
        self.assert_(not f.has_default())
        self.assertEqual('', f.get_default())

    def test_generate_value_char_field(self):
        f = models.CharField(blank=False,null=False)
        self.assertEqual('', milkman.value_for(f))
    
    def test_should_deliver(self):
        assert not milkman.is_deliverable(models.CharField())
        assert milkman.is_deliverable(models.ManyToManyField(Uncle))
        assert milkman.is_deliverable(models.ManyToManyField(Aunt))
        

class MilkmanUtilFuncTest(unittest.TestCase):
    def test_random_str(self):
        self.assertEqual(8, len(milkman.random_string()))
        self.assertEqual('a' * 8, milkman.random_string(chars=['a']))
        class Foo: 
            max_length = 10
        self.assertEqual('a' * 10, milkman.random_string(Foo, ['a']))
        
    def test_gen(self):
        self.assertEqual([''],[x for x in milkman.gen()])
        self.assertEqual([1],[x for x in milkman.gen([1])])
        self.assertEqual(['', ''], [s for s in milkman.gen(size=2)])
        self.assertEqual([1, 1], [s for s in milkman.gen([1], 2)])
        