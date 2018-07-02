# Test cases for OxygenRM Models

import unittest
from OxygenRM.internals.columns import *

class T():
    t = Text()
    b = Bool()
    i = Integer()
    f = Float()
    id = Id()

class TestColumns(unittest.TestCase):
    def test_all_columns_classes_initialize(self):
        t = Text()
        b = Bool()

        self.assertIsInstance(t, Text)
        self.assertIsInstance(b, Bool)
        
    def test_text_valid_values_set_and_get(self):
        t = T()
        t.t = 'a'

        self.assertEqual(t.t, 'a')
        self.assertIsInstance(t.t, str)    

    def test_text_unvalid_set_raises_typeError(self):
        t = T()

        with self.assertRaises(TypeError):
            t.t = 1

        with self.assertRaises(TypeError):
            t.t = False

        with self.assertRaises(TypeError):
            t.t = T

    def test_bool_has_no_problem_with_bools(self):
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
        t = T()

        with self.assertRaises(TypeError):
            t.b = 3

        with self.assertRaises(TypeError):
            t.b = []

        with self.assertRaises(TypeError):
            t.b = None        

    def test_int_raises_TypeError(self):
        t = T()

        with self.assertRaises(TypeError):
            t.i = True

        with self.assertRaises(TypeError):
            t.i = 3.4

        with self.assertRaises(TypeError):
            t.i = None        

    def test_int_validation(self):
        t = T()

        t.i = 1
        self.assertEqual(t.i, 1)

        t.i = 18231
        self.assertEqual(t.i, 18231)
    
    def test_float_raises_TypeError(self):
        t = T()

        with self.assertRaises(TypeError):
            t.f = set()

        with self.assertRaises(TypeError):
            t.f = {}

        with self.assertRaises(TypeError):
            t.f = 'That'        

    def test_float_validation(self):
        t = T()

        t.f = 1
        self.assertEqual(t.f, 1.0)

        t.f = 123.2
        self.assertEqual(t.f, 123.2)

    def test_id_cannot_be_reassigned(self):
        t = T()

        with self.assertRaises(AttributeError):
            t.id = 23

    def test_rel_prop_creation(self):
        pass

    def test_id_prop_creation(self):
        pass

    def test_email_prop_creation(self):
        pass

    def test_json_prop_creation(self):
        pass

    def test_date_prop_creation(self):
        pass

    def test_float_prop_creation(self):
        pass