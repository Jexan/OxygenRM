from . import *

class JsonModel(O.Model):
    a = JSON()

class TestJSONFields(unittest.TestCase):
    def setUp(self):
        db.create_table('JsonModels', default_cols(a='json'))

    def tearDown(self):
        db.drop_table('JsonModels')

    def test_model_initialization(self):
        t1 = JsonModel()

        self.assertIsInstance(t1.a, dict)

    def test_json_setting_up_a_container(self):
        t1 = JsonModel()

        t1.a = []
        self.assertIsInstance(t1.a, list)
        self.assertTrue(t1.a.conformable)

    def test_complex_json(self):
        t1 = JsonModel()

        t1.a[1] = 2
        t1.a[4] = 4

        self.assertEqual(t1.a, {1:2, 4:4})

    def test_saving_json(self):
        t1 = JsonModel()
        t1.a = [1,2,3]
        t1.save()

        result = QueryBuilder.table('JsonModels').first()

        self.assertEqual(result['a'], t1.a.to_json())

    def test_getting_loaded_json(self):
        db.create('jsonmodels', a=json.dumps([1,2,3]))

        first = JsonModel.first()

        self.assertEqual(first.a, [1,2,3])

    def test_setting_pure_json(self):
        t1 = JsonModel()
        t1.a = json.dumps([1,2,3])
        t1.save()

        result = QueryBuilder.table('JsonModels').first()

        self.assertEqual(result['a'], t1.a.to_json())