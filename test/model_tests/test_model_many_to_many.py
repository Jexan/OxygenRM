from . import *

class T1(O.Model):
    id = Id()

class T2(O.Model):
    id = Id()
    t1s = Multiple(T1)
    
T1.t2s = Multiple(T2)

T1.set_up()
T2.set_up()

ts_cols = next(default_cols(id='integer'))._replace(primary=True, auto_increment=True)

class TestManyToMany(unittest.TestCase):
    def setUp(self):
        db.drop_table('t1s')
        db.drop_table('t2s')
        db.drop_table('t1_t2')
        
        db.create_table('t1s', (ts_cols, ))
        db.create_table('t2s', (ts_cols, ))
        db.create_table('t1_t2', default_cols(t1_id='integer', t2_id='integer'))

    def test_initialization_ok(self):
        self.assertIsInstance(T1(), T1)
        self.assertIsInstance(T2(), T2)

        self.assertIsInstance(T1.t2s, property)
        self.assertIsInstance(T2.t1s, property)

    def test_many_to_many_with_one_works(self):
        db.create('t1s', id=1)
        db.create('t2s', id=1)
        db.create('t1_t2', t1_id=1, t2_id=1)

        first_t1 = T2.first().t1s.first()
        self.assertEqual(first_t1.id, 1)

        first_t2 = T1.first().t2s.first()
        self.assertEqual(first_t2.id, 1)

    def test_many_to_many_with_zero_its_an_empty_collection(self):
        db.create('t1s', id=1)
        db.create('t2s', id=1)

        first_t2 = T1.first().t2s
        self.assertEqual(len(first_t2), 0)

        first_t1 = T2.first().t1s
        self.assertEqual(len(first_t1), 0)

    def test_many_to_many_with_multiple_work(self):
        db.create('t1s', id=1)
        db.create_many('t2s', ('id',), ((i,) for i in range(1, 4)))
        db.create_many('t1_t2', ('t1_id', 't2_id'), ((1, i) for i in range(1, 4)))

        t2s = T1.first().t2s

        self.assertEqual(len(t2s), 3)
        self.assertEqual(len(set(t2s.pluck('id'))), 3)
        self.assertTrue(all(t2.t1s.first().id == 1 for t2 in t2s))

    def test_many_to_many_with_dummies_work(self):
        db.create('t1s', id=1)
        db.create_many('t2s', ('id',), ((i,) for i in range(1, 3)))
        db.create_many('t1_t2', ('t1_id', 't2_id'), ((1, i) for i in range(1, 10)))

        t2s = T1.first().t2s

        self.assertEqual(len(t2s), 2)

        ids = list(t2s.pluck('id'))
        self.assertEqual(len(set(ids)), 2)
        self.assertEqual(ids, [1, 2])
        self.assertTrue(all(t2.t1s.first().id == 1 for t2 in t2s))
