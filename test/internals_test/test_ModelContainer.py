import unittest
from json import dump

from OxygenRM.internals.ModelContainer import *
from OxygenRM.models import Model

from .. import db
from . import default_cols

class Test(Model):
    pass

# A container for models
class TestModelContainer(unittest.TestCase):
    def tearDown(self):
        db.drop_all_tables()

    def setUp(self):
        db.create_table('tests', default_cols(a='text'))
        db.create_many('tests', ('a', ), ('a', 'b', 'c'))
        self.mc = ModelContainer(db.all('tests'), Test)
        
    def test_model_initiliaziation(self):
        mc = ModelContainer([], Test)

        self.assertIsInstance(mc, ModelContainer)
        self.assertEqual(mc._model, Test)

    def test_iterable_properties(self):
        for row in self.mc:
            self.assertIsInstance(row, self.mc._model)
        
    def test_json_conversion(self):
        json_data = self.mc.to_json()
        expected = '[{"a": "a"}, {"a": "b"}, {"a": "c"}]'

        self.assertEqual(json_data, expected)

    def test_csv_conversion(self):
        pass
    
    def test_xml_conversion(self):
        pass
        
    def test_first(self):
        first = self.mc.first()
        self.assertEqual(first.a, 'a')
        
    def test_distinct_actually_gives_distinct(self):
        db.create_many('tests', ('a', ), ('a', 'a'))
        distinct = self.mc.distinct()
        counter = {'a':0, 'b':0, 'c':0}

        for row in distinct:
            counter[row.a] += 1

        self.assertEqual(counter['a'], 1)
        self.assertEqual(counter['b'], 1)
        self.assertEqual(counter['c'], 1)
    
    def test_list_conversion(self):
        as_list = self.mc.to_list()

        self.assertEqual(len(as_list), 3)
        self.assertIsInstance(as_list, list)

    def test_getting_index_yields_list(self):
        item = self.mc[1]

        self.assertEqual(item.a, 'b')
        
    def test_pluck(self):
        aes = self.mc.pluck('a')
        self.assertEqual(['a', 'b', 'c'], list(aes))
                
    def test_model_pretty(self):
        pretty_str = self.mc.pretty()
        self.assertEqual(pretty_str, 'Test:\n\t1:\n\t\ta: a\n\t2:\n\t\ta: b\n\t3:\n\t\ta: c\n')

    # FOR SOME REASON THIS TEST FAILED IF WE ADDED THE WORD 'DICT' TO IT
    def test_to_dict_container(self):
        cont_as_dict = list(self.mc.to_dict())

        self.assertEqual(len(cont_as_dict), 3)
        self.assertEqual(cont_as_dict, [{'a': 'a'}, {'a': 'b'}, {'a': 'c'}])