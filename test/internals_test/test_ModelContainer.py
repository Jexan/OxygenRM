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

    def test_iterator_is_not_shared_behaves_as_expected(self):
        one_list = []
        two_list = []

        one_list.extend(self.mc)
        two_list.extend(self.mc)

        self.assertEqual(len(one_list), 3)
        self.assertNotEqual(len(two_list), 0)
        self.assertEqual(len(two_list), 3)
            
    def test_list_conversion(self):
        as_list = list(self.mc)

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