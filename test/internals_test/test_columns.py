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
        """ Assure the columns classes constructor work
        """
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