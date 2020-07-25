# Test case for OxygenRM Models with columns

import unittest
from OxygenRM.internals.fields import *
from OxygenRM.models import *

types = {'t': Text(), 'b': Bool(), 'i': Integer(), 'f': Float(), 'id': Id()}

class T(Model):
    t = Text()
    b = Bool()
    i = Integer()
    f = Float()
    id = Id()

class TestFields(unittest.TestCase):
    def test_all_columns_classes_initialize(self):
        """ Test all columns initialize correctly, even outside a class.
        """
        t = Text()
        b = Bool()

        self.assertIsInstance(t, Text)
        self.assertIsInstance(b, Bool)
        
    def test_text_valid_values_set_and_get(self):
        """ Assure the setter and getter for the text field 
            works as expected.
        """
        t = T()
        t.t = 'a'

        self.assertEqual(t.t, 'a')
        self.assertIsInstance(t.t, str)    

    def test_text_unvalid_set_raises_typeError(self):
        """ Assure that a TypeError will be thrown by a Text field
            if a non-str value is attempt to be set.
        """
        t = T()

        with self.assertRaises(TypeError):
            t.t = 1

        with self.assertRaises(TypeError):
            t.t = False

        with self.assertRaises(TypeError):
            t.t = T

    def test_bool_has_no_problem_with_bools(self):
        """ Check the bool field accepts True, False,
            0 and 1 as valid values.
        """
        t = T()

        t.b = True
        self.assertTrue(t.b)
        
        t.b = False
        self.assertFalse(t.b)

        t.b = 1
        self.assertEqual(t.b, True)

        t.b = 0
        self.assertEqual(t.b, False)

    def test_bool_raises_if_set_not_bool(self):
        """ Check that bool fields will throw a TypeError
            if the value is not a bool.
        """
        t = T()

        with self.assertRaises(TypeError):
            t.b = 3

        with self.assertRaises(TypeError):
            t.b = []

        with self.assertRaises(TypeError):
            t.b = None        

    def test_int_raises_TypeError(self):
        """ Assert a int field won't accept booleans
            or floats.
        """
        t = T()

        with self.assertRaises(TypeError):
            t.i = True

        with self.assertRaises(TypeError):
            t.i = 3.4

    def test_int_validation(self):
        """ Assert the int field setter works with ints.
        """
        t = T()

        t.i = 1
        self.assertEqual(t.i, 1)

        t.i = 18231
        self.assertEqual(t.i, 18231)
    
    def test_float_raises_TypeError(self):
        """ Assure float field validation will throw an error
            if not float.
        """
        t = T()

        with self.assertRaises(TypeError):
            t.f = set()

        with self.assertRaises(TypeError):
            t.f = {}

        with self.assertRaises(TypeError):
            t.f = 'That'        

    def test_float_validation(self):
        """ Assure float field validation works.
        """
        t = T()

        t.f = 1
        self.assertEqual(t.f, 1.0)

        t.f = 123.2
        self.assertEqual(t.f, 123.2)

    def test_rel_prop_creation(self):
        ...

    def test_id_prop_creation(self):
        ...

    def test_email_prop_creation(self):
        ...

    def test_json_prop_creation(self):
        ...

    def test_date_prop_creation(self):
        ...

    def test_float_prop_creation(self):
        ...