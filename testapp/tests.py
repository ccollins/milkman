import unittest
import types
import sys
import string
from django.db import models
from milkman.dairy import milkman
from milkman.dairy import MilkTruck
from milkman.generators import email_generator, random_choice_iterator, random_string, random_float, random_ipaddress_maker, random_float_maker,random_comma_seperated_integer_maker, random_time_string_maker
from testapp.models import *

MODELS = [Root, Child, Uncle]
class ModelTest(unittest.TestCase):
    def tearDown(self):
        for m in MODELS:
            m._default_manager.all().delete()
    
    def test_create(self):
        r = milkman.deliver(Root)
        self.assertEqual(Root, r.__class__)
        self.assertTrue(bool(r.my_auto))
        assert r.my_char is not None

    def test_create_with_string(self):
        r = milkman.deliver('testapp.Root')
        self.assertEqual(Root, r.__class__)
        self.assertTrue(bool(r.my_auto))
        assert r.my_char is not None

    def test_create_explicit(self):
        r = milkman.deliver(Root, my_char='foo')
        self.assertEqual('foo', r.my_char)

    def test_create_child(self):
        child = milkman.deliver(Child)
        assert child.root
    
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
    
    def test_m2m_explicit(self):
        uncle = milkman.deliver(Uncle)
        aunt = milkman.deliver(Aunt, uncles=[uncle])
        self.assertEquals(uncle, aunt.uncles.all()[0])
    
    def test_m2m_through_model(self):
        couseling_uncle = milkman.deliver(CounselingUncle)
        self.assertTrue(isinstance(couseling_uncle, CounselingUncle))
        self.assertEquals(couseling_uncle.cousin.uncles.all().count(), 1)
        self.assertTrue(len(couseling_uncle.cousin.name) > 0)
        self.assertTrue(len(couseling_uncle.uncle.name) > 0)
    
    def test_m2m_model(self):
        child = milkman.deliver(EstrangedChild)
        self.assertTrue(isinstance(child, EstrangedChild))
        self.assertEquals(child.uncles.all().count(), 0)
        self.assertTrue(len(child.name) > 0)
    
    def test_m2m_model_explicit_add(self):
        child = milkman.deliver(EstrangedChild)
        couseling_uncle = milkman.deliver(CounselingUncle, cousin=child)
        self.assertTrue(isinstance(child, EstrangedChild))
        self.assertEquals(child.uncles.all().count(), 1)
        self.assertTrue(len(child.name) > 0)
        
    def test_m2m_model_self(self):
        child = milkman.deliver(PsychoChild)
        self.assertEquals(child.alter_egos.all().count(), 1)
        self.assertEquals(PsychoChild.objects.all().count(), 2)

    def test_related_explicit_values(self):
        child = milkman.deliver(Child, root__my_char='foo')
        self.assertEqual(child.root.my_char, 'foo')

        grandchild = milkman.deliver(GrandChild, parent__name='foo', parent__root__my_char='bar')
        self.assertEqual(grandchild.parent.name, 'foo')
        self.assertEqual(grandchild.parent.root.my_char, 'bar')

        root = milkman.deliver(Root)
        grandchild = milkman.deliver(GrandChild, parent__root=root)
        self.assertEqual(root.pk, grandchild.parent.root.pk)

    def test_m2m_related_explicit_values(self):
        aunt = milkman.deliver(Aunt, uncles__name='foo')
        self.assertEqual(1, len(aunt.uncles.all()))
        self.assertEqual(aunt.uncles.all()[0].name, 'foo')

    def test_image_model(self):
        image = milkman.deliver(ImageChild)
        self.assertTrue(len(image.photo.url) > 0)
        self.assertTrue(image.photo.size > 0)



INHERITED_MODELS = [AdoptedChild]
class ModelInheritanceTest(unittest.TestCase):
    def tearDown(self):
        for m in INHERITED_MODELS:
            m._default_manager.all().delete()
    
    def test_create_adopted_child(self):
        a = milkman.deliver(AdoptedChild)
        assert a.root is not None

class RandomFieldTest(unittest.TestCase):
    def test_required_field(self):
        root = milkman.deliver(Root)
        assert isinstance(root.my_auto, int)
        try:
            assert isinstance(root.my_biginteger, type(models.BigIntegerField.MAX_BIGINT))
        except AttributeError:
            pass
        assert isinstance(root.my_boolean, bool)
        assert isinstance(root.my_char, str)
        assert isinstance(root.my_commaseperatedinteger, str)
        assert isinstance(root.my_date, str)
        assert isinstance(root.my_datetime, str)
        assert isinstance(root.my_decimal, str)
        assert isinstance(root.my_email, str)
        assert isinstance(root.my_float, float)
        assert isinstance(root.my_integer, int)
        assert isinstance(root.my_ip, str)
        assert (isinstance(root.my_nullboolean, bool) or isinstance(root.my_nullboolean, types.NoneType))
        assert isinstance(root.my_positiveinteger, int)
        assert isinstance(root.my_positivesmallinteger, int)
        assert isinstance(root.my_slug, str)
        assert isinstance(root.my_smallinteger, int)
        assert isinstance(root.my_text, str)
        assert isinstance(root.my_time, str)
    
class FieldTest(unittest.TestCase):
    def test_needs_generated_value(self):
        f = Root._meta.get_field('my_char')
        assert MilkTruck(None).needs_generated_value(f)
        assert not f.has_default()
        self.assertEqual('', f.get_default())

class FieldValueGeneratorTest(unittest.TestCase):
    def test_email_generator(self):
        f = models.EmailField()
        g = email_generator('test', 'fake.com')(f)()
        self.assertEquals('test1@fake.com', g.next())
        self.assertEquals('test2@fake.com', g.next())

    def test_random_str(self):
        self.assertEqual(8, len(random_string()))
        self.assertEqual('a' * 8, random_string(chars=['a']))
        self.assertEqual('a' * 10, random_string(10, ['a']))
        
    def test_random_choice_iterator(self):
        self.assertEqual([''],[x for x in random_choice_iterator()])
        self.assertEqual([1],[x for x in random_choice_iterator([1])])
        self.assertEqual(['', ''], [s for s in random_choice_iterator(size=2)])
        self.assertEqual([1, 1], [s for s in random_choice_iterator([1], 2)])
        
    def test_random_float(self):
        assert random_float() >= sys.float_info.min
        assert random_float() <= sys.float_info.max
        assert isinstance(random_float(), float)
        
    def test_random_ipaddress(self):
        f = models.IPAddressField()
        ip = random_ipaddress_maker(f)().next()
        ip = ip.split('.')
        self.assertEquals(len(ip), 4)
        
    def test_random_comma_seperated_integer_maker(self):
        f = models.CommaSeparatedIntegerField()
        v = random_comma_seperated_integer_maker(f)().next()
        self.assertEquals(len(v.split(',')), 4)
        
    def test_timefield_maker(self):
        f = models.TimeField()
        v = random_time_string_maker(f)().next()
        times = v.split(':')
        self.assertEquals(len(times), 3)

    def test_field_name_clash(self):
        milkman.deliver(LongName)
        short_name = milkman.deliver(ShortName)

        self.assertEqual(len(short_name.name), 100)

