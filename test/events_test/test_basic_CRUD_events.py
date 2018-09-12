from . import *

class TestEventsHook(unittest.TestCase):
    def setUp(self):
        test = Table('test')
        test.a = c.Text()
        test.create()

    def tearDown(self):
        event.drop_all_events()
        Table.drop_all()

    @classmethod
    def tearDownClass(cls):
        cancel_events()

    @classmethod
    def setUpClass(cls):
        use_events()

    def test_db_access_event(self):
        @event.listen('db.operation_perfomed', 1)
        def t(query, values):
            self.assertTrue('SELECT' in query)

        db.all('test')
        self.assertEqual(t.times, 0)

    def test_db_query_called(self):
        @event.listen('db.operation_called', 1)
        def t(query, values):
            self.assertTrue('SELECT' in query)

        db.all('test')
        self.assertEqual(t.times, 0)

    def test_db_insert_event_triggers(self):
        @event.listen('db.created_record', 1)
        def t(table_name, **values):
            self.assertTrue(table_name == 'test' and values['a'] == 't')

        db.create('test', a='t')
        self.assertEqual(t.times, 0)

    def test_event_table_creation(self):
        @event.listen('db.created_table', 1)
        def t(table_name, columns): 
            self.assertTrue(table_name == 'test2' and tuple(columns)[0].name == 'a')

        with Table('test2') as test:
            test.a = c.Text()
        self.assertEqual(t.times, 0)

    def test_event_table_droppage(self):
        @event.listen('db.dropped_table', 1)
        def t(table_name):
            self.assertTrue(table_name == 'test2')

        with Table('test2') as test:
            test.a = c.Text()

        Table('test2').drop()
        self.assertEqual(t.times, 0)

    def test_event_table_renaming(self):        
        @event.listen('db.renamed_table', 1)
        def t(old_name, new_name): 
            self.assertTrue(old_name == 'test' and new_name == 'test2')
        
        test = Table('test')
        test.rename('test2')
        test.save()
        self.assertEqual(t.times, 0)

    def test_event_table_truncate(self):        
        @event.listen('db.truncated_table', 1)
        def t(table): 
            self.assertTrue(table == 'test')

        db.truncate('test')
        self.assertEqual(t.times, 0)

    def test_event_drop_all_tables(self):
        self.flag = False
        @event.listen('db.all_tables_dropped', 1)
        def t():
            self.flag = True

        db.drop_all_tables()
        self.assertEqual(t.times, 0)
        self.assertTrue(self.flag)

    def test_event_transactions(self):
        self.flag = 0
        @event.listen('db.transaction_started', 1)
        def t1(): 
            self.flag += 1
        
        @event.listen('db.transaction_ended', 1)
        def t2(): 
            self.flag += 1

        with db.transaction(): 
            1 + 2

        self.assertEqual(self.flag, 2)
        self.assertEqual(t1.times, 0)
        self.assertEqual(t2.times, 0)

    def test_event_transaction_failed(self):        
        @event.listen('db.transaction_failed', 1)
        def t(exception): 
            self.assertIsInstance(exception, ValueError)

        try:
            with transaction(): raise ValueError('Test')
        except ValueError as E: pass

        self.assertEqual(t.times, 0)

# @event.models.operation
# def t(instance, query): pass

# @event.models.get
# def t(instance, collection, query): pass

# @event.models.saved_model
# def t(instance, collection, is_new): pass

# @event.model.new_model
# def t(instance): pass

# @event.model.edited_model
# def t(instance): pass

# @event.model.delete
# def t(instance): pass

# @event.model.get_pivot
# def t(instance, pivot): pass

# event.remove(event.model.get_pivot)
# t.remove()
# @event.replace(event.model.get_pivot, times=2)
# def t(*): pass

# t.run_times = 2
# t.run_times += 0

# # @Model.event.*all_above
# # def t(*): pass
# # 
# # @instance.event.*all_above
# # def t(*): pass
