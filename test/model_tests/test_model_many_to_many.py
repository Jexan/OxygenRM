from . import *

class T1(O.Model):
    id = Id()

class T2(O.Model):
    id = Id()
    t1s = Multiple(T1)
    
T1.t2s = Multiple(T2)

T1.set_up()
T2.set_up()

ts_cols = (id_col, )
middle_cols = tuple(default_cols(t1_id='integer', t2_id='integer'))

def create_to_id(table, max_id=1):
    db.create_many(table, ('id', ), ((i, ) for i in range(1, max_id+1)))

def assoc_ids_with_iter(ids_gen):
    db.create_many('t1_t2', ('t1_id', 't2_id'), tuple(ids_gen))

class TestManyToMany(unittest.TestCase):
    def setUp(self):
        db.drop_table('t1s')
        db.drop_table('t2s')
        db.drop_table('t1_t2')
        
        db.create_table('t1s', ts_cols)
        db.create_table('t2s', ts_cols)
        db.create_table('t1_t2', middle_cols)

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

    def test_many_to_many_assign(self):
        db.create('t1s', id=1)
        db.create('t2s', id=1)

        t2 = T2.first()
        T1.first().rel('t2s').assign(t2).save()

        self.assertEqual(len(T1.first().t2s), 1)        
        self.assertEqual(len(T2.first().t1s), 1)

    def test_many_to_many_assign_many(self):
        db.create('t1s', id=1)
        create_to_id('t2s', 5)

        T1.first().rel('t2s').assign_many(T2.all()).save()

        self.assertEqual(len(T1.first().t2s), 5)
        self.assertEqual(len(set(T1.first().t2s.pluck('id'))), 5)

    def test_many_to_many_assign_resets_assigns(self):
        db.create('t1s', id=1)
        create_to_id('t2s', 5)
        assoc_ids_with_iter((1, i) for i in range(1, 4))

        t2 = T2.find(5)
        T1.first().rel('t2s').assign(t2).save()

        self.assertEqual(len(T1.first().t2s), 1)        
        self.assertEqual(len(T2.find(5).t1s), 1)        

    def test_many_to_many_deassign(self):
        db.create('t1s', id=1)
        db.create('t2s', id=1)
        db.create('t1_t2', t1_id=1, t2_id=1)

        T1.first().rel('t2s').deassign(T2.first()).save()

        self.assertEqual(len(T1.first().t2s), 0)   

    def test_many_to_many_deassignal(self):
        db.create('t1s', id=1)
        db.create('t2s', id=1)
        db.create('t1_t2', t1_id=1, t2_id=1)

        T1.first().rel('t2s').deassign_all().save()

        self.assertEqual(len(T1.first().t2s), 0)   

    def test_many_to_many_add(self):
        db.create('t1s', id=1)
        create_to_id('t2s',3)
        db.create('t1_t2', t1_id=1, t2_id=2)

        t2 = T2.first()
        T1.first().rel('t2s').add(t2).save()

        assoc_t2s = T1.first().t2s

        self.assertEqual(len(assoc_t2s), 2)        
        self.assertEqual(len(T2.first().t1s), 1)

        for row in assoc_t2s:
            self.assertIn(row.id, (1, 2))

    def test_many_to_many_add_many(self):
        db.create('t1s', id=1)
        create_to_id('t2s',3)
        db.create('t1_t2', t1_id=2, t2_id=2)

        T1.first().rel('t2s').add_many(T2.all()).save()

        assoc_t2s = T1.first().t2s

        self.assertEqual(len(assoc_t2s), 3)        
        self.assertEqual(tuple(assoc_t2s.pluck('id')), (1, 2, 3))

    def test_many_to_many_eager_load(self):
        create_to_id('t1s', 3)
        create_to_id('t2s', 3)
        db.create('t1_t2', t1_id=1, t2_id=3)
        db.create('t1_t2', t1_id=2, t2_id=1)
        db.create('t1_t2', t1_id=2, t2_id=2)

        t1s = T1.with_relations('t2s').get()

        self.assertEqual(len(t1s[0].t2s), 1)
        self.assertEqual(len(t1s[1].t2s), 2)
        self.assertEqual(len(t1s[2].t2s), 0)

    def test_many_to_many_lazy_loading(self):
        create_to_id('t1s', 2)
        create_to_id('t2s', 3)
        db.create('t1_t2', t1_id=1, t2_id=3)
        db.create('t1_t2', t1_id=2, t2_id=1)
        db.create('t1_t2', t1_id=2, t2_id=2)

        t1s = T1.all()

        t1s.load('t2s')

        self.assertEqual(len(t1s[0].t2s), 1)
        self.assertEqual(len(t1s[1].t2s), 2)
