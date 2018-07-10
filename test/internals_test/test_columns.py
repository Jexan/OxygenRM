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
        i = Integer()
        f = Float()
        i_d = Id()

        self.assertIsInstance(t, Text)
        self.assertIsInstance(b, Bool)
        self.assertIsInstance(i, Integer)
        self.assertIsInstance(f, Float)
        self.assertIsInstance(i_d, Id)
        
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