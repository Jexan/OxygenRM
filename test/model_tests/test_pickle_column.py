from . import *

import pickle

class PickleModel(O.Model):
    a = Pickle()
    b = Pickle(list, strict=True)
    c = Pickle(int)
    d = Pickle(dict, ({'t': 1},))

class TestJSONFields(unittest.TestCase):
    def setUp(self):
        db.create_table('PickleModels', default_cols(a='blob', b='blob', c='blob', d='blob'))

    def tearDown(self):
        db.drop_table('PickleModels')

    def test_model_initialization(self):
        t1 = PickleModel()

        self.assertIs(t1.a, None)
        self.assertIsInstance(t1.b, list)
        self.assertIsInstance(t1.c, int)
        self.assertIsInstance(t1.d, dict)

        self.assertEqual(t1.b, [])
        self.assertEqual(t1.c, 0)
        self.assertEqual(t1.d, {'t': 1})

    def test_model_strict_changing_raises_TypeError(self):
        t1 = PickleModel()

        with self.assertRaises(TypeError):
            t1.b = 42

    def test_model_setting(self):
        t1 = PickleModel()

        t1.a = None
        t1.c = 2.3
        t1.d = False

        self.assertEqual(t1.a, None)
        self.assertEqual(t1.c, 2.3)
        self.assertEqual(t1.d, False)

    def test_saving_pickle_defaults(self):
        t1 = PickleModel()
        t1.save()

        result = QueryBuilder.table('PickleModels').first()

        self.assertEqual(result['a'], pickle.dumps(t1.a))
        self.assertEqual(result['b'], pickle.dumps(t1.b))
        self.assertEqual(result['c'], pickle.dumps(t1.c))
        self.assertEqual(result['d'], pickle.dumps(t1.d))

    def test_getting_loaded_picle(self):
        t1 = PickleModel()
        t1.save()

        first = PickleModel.first()

        self.assertEqual(first.a, None)
        self.assertEqual(first.b, [])
        self.assertEqual(first.d, {'t': 1})

    def test_setting_pure_bytes(self):
        t1 = PickleModel()
        t1.a = pickle.dumps([1,2,3])
        t1.save()

        result = QueryBuilder.table('PickleModels').first()

        self.assertEqual(result['a'], pickle.dumps([1,2,3]))