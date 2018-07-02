# Test cases for OxygenRM Models

import unittest
from OxygenRM.internals.columns import *

class T():
    t = Text()
    b = Bool()

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
        self.assertEqual(t.b, 1)

        t.b = 0
        self.assertEqual(t.b, 0)

        t.b = 4


    def test_bool_raises_if_set_not_bool(self):
        t = T()

        with self.assertRaises(TypeError):
            t.b = 3

        with self.assertRaises(TypeError):
            t.t = []

        with self.assertRaises(TypeError):
            t.t = None        

    def test_int_prop_creation(self):
        pass

    def test_text_prop_creation(self):
        pass

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