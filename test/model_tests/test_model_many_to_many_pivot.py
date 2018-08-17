from . import *

from OxygenRM.pivot import Pivot 

class Pivot(Pivot):
    t1_id = Integer()
    t2_id = Integer()

    pivot1 = Text()
    pivot2 = Integer()
    pivot3 = Bool()
    pivot4 = Date(update_date=True)

class T1(O.Model):
    id = Id()

    @classmethod
    def relations(cls):
        cls.t2s = Multiple(T2, pivot=Pivot)

class T2(O.Model):
    id = Id()

    @classmethod
    def relations(cls):
        cls.t1s = Multiple(T2, pivot=Pivot)    

T2.set_up()
T1.set_up()

ts_cols = (id_col, )
middle_cols = tuple(default_cols(t1_id='integer', t2_id='integer', pivot1='text', pivot2='integer', pivot3='boolean', pivot4='date'))

def create_to_id(table, max_id=1):
    db.create_many(table, ('id', ), ((i, ) for i in range(1, max_id+1)))

def assoc_ids_with_iter(ids_gen):
    db.create_many('t1_t2', ('t1_id', 't2_id'), tuple(ids_gen))

def create_basic_pivot():
    pivot = T1.pivots('t2s').new()
    pivot.t1_id = 1  
    pivot.t2_id=1  
    pivot.pivot3=True  
    pivot.pivot2=10
    pivot.save()

class TestManyToManyPivot(unittest.TestCase):
    def setUp(self):
        db.drop_table('t1s')
        db.drop_table('t2s')
        db.drop_table('t1_t2')
        
        db.create_table('t1s', ts_cols)
        db.create_table('t2s', ts_cols)
        db.create_table('t1_t2', middle_cols)

    def test_initialization_ok(self):
        half_pivot = T1.pivots('t2s').new()

        self.assertIsInstance(half_pivot, Pivot)

    def test_pivot_creating_saving_works(self):
        create_basic_pivot()
        result = T1.pivots('t2s').first()

        self.assertEqual(result.t1_id, 1)
        self.assertEqual(result.pivot3, True)

    @unittest.skip('Not yet implemented')
    def test_pivot_updating_and_searching(self):
        create_basic_pivot()
        pivot = T1.pivots('t2s').first()

        self.assertEqual(result['t1_id'], 1)
        self.assertEqual(result['pivot3'], True)

    def test_new_model_with_pivot_saving(self):
        model = T1()
        model.t2s.pivot.pivot3 = False

        with self.assertRaises(ValueError):
            model.save()

        model.t2s.pivot.t2_id = 1
        model.save()

        result = next(db.all('t1_t2'))

        self.assertEqual(result['t1_id'], 1)
        self.assertEqual(result['t2_id'], 1)
        self.assertFalse(result['pivot3'])

    def test_pivot_access(self):
        create_basic_pivot()
        db.create('t2s', id=1)
        db.create('t1s', id=1)

        model = T1.first()
        pivot_model = model.t2s.first().pivot

        self.assertEqual(pivot_model.t1_id, 1)
        self.assertEqual(pivot_model.t2_id, 1)
        self.assertTrue(pivot_model.pivot3)

    @unittest.skip('Not yet implemented')
    def test_where_pivot(self):
        create_basic_pivot()
        db.create('t2s', id=1)

        modelq1 = T1.pivots('t2s').where_pivot('pivot2', '=', True).get()
        modelq2 = T1.pivots('t2s').where_pivot('pivot2', '=', False).get()

        self.assertEqual(len(modelq1), 1)
        self.assertEqual(len(modelq2), 0)

    