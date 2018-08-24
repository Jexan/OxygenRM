from . import *

class Todo(O.Model):
    a = Text()

Todo.set_up()

def todo_with_id():
    todos = Table('todos')
    todos.id = c.Id()
    todos.save()

    class Todo(O.Model):
        a = Text()
        id = Id()

    return Todo

def first_todo():
    return db.all('todos').fetchone()

def create_todo():
    db.create('todos', a='t')

class TestModels(unittest.TestCase):
    def tearDown(self):
        db.drop_all_tables()

    def setUp(self):
        db.create_table('todos', default_cols(a='text'))

    def test_model_initializes_correctly(self):
        t = Todo()

        self.assertIsInstance(t, Todo)
        self.assertIsInstance(t, O.Model)
    
    def test_model_field_set_ups_correctly_and_fields_work_ok(self):
        t = Todo()
        t.a = 'hey'
        self.assertEqual(t.a, 'hey')

        with self.assertRaises(TypeError):
            t.a = 12

    def test_model_can_have_custom_table_name(self):
        db.create_table('murder', default_cols(name='text'))
        class Crow(O.Model):
            table_name = 'murder'

            name = Text()

        Crow()

        self.assertEqual(Crow.table_name, 'murder')

    def test_model_where_queries(self):
        create_todo()

        self.assertEqual(Todo.where('a', '=', 't').get().first().a, first_todo()['a'])

    def test_fetching_multiple_models(self):
        create_todo()
        create_todo()

        t = Todo.first()
        t.a = 's'

        e = Todo.all()[1]
        e.a = 't'

        self.assertNotEqual(t.a, e.a)

    def test_model_properties_are_not_shared_between_instances(self):
        class R:
            pass

        R.e = Integer()
        a = R()
        b = R()

        a.e = 1
        b.e = 3

        self.assertNotEqual(a, b)

    def test_model_querying_limit(self):
        for i in range(100): create_todo()

        self.assertEqual(len(Todo.limit(50).get()), 50)

    def test_models_new_and_saving_creates_record_in_db(self):
        t = Todo()
        t.a = 't'
        t.save()

        record = db.all('todos').fetchone()
        self.assertEqual(record['a'], 't')

        s = Todo()
        t.a = 't2'

        self.assertEqual(t.a, 't2')
        t.save()

        record = list(db.all('todos'))[-1]
        self.assertEqual(record['a'], 't2')

    def test_model_craft_model_with_id_column_returns_model_itself(self):
        Todo = todo_with_id()

        t = Todo.craft(a='t')
        self.assertEqual(t.a, 't')
        
        self.assertEqual(first_todo()['a'], 't')
    
    def test_model_craft_with_no_model_to_be_returned_returns_true(self):
        self.assertTrue(Todo.craft(False, a='t'))
        
        self.assertEqual(first_todo()['a'], 't')

    def test_models_craft_with_model_with_no_primary_key_returns_no_model(self):
        self.assertTrue(Todo.craft(a='t'))

    def test_models_delete_one_instance(self):
        create_todo()

        Todo.where('a', '=', 't').first().delete()

        self.assertIs(None, first_todo())

    def test_models_delete_all_records(self):
        create_todo()

        t = Todo.where('a', '=', 't').delete()

        self.assertIs(None, first_todo())

    def test_models_destroy(self):
        Todo = todo_with_id()
        create_todo()

        Todo.destroy(1)

        self.assertIs(None, first_todo())

    def test_models_table_truncate_deletes_all_redcords(self):
        db.create_many('todos', ['a'], zip(range(10)))
        Todo.truncate()

        self.assertIs(None, first_todo())

    def test_model_fetch_and_update_saving(self):
        create_todo()

        t = Todo.where('a', '=', 't').first()
        t.a = 's'
        t.save()

        all_records = list(db.all('todos'))
        self.assertEqual(len(all_records), 1)

        record = all_records[0]

        self.assertEqual(record['a'], 's')

    def test_model_new_updates_the_working_model(self):
        Todo = todo_with_id()

        t = Todo()
        self.assertEqual(t.id, None)

        t.save()
        self.assertEqual(t.id, 1)

class TestModelSettingUp(unittest.TestCase):
    def setUp(self):
        class Todo(O.Model):
            a = Text()

        self.Todo = Todo

        db.create_table('todos', default_cols(a='text'))

    def tearDown(self):
        db.drop_table('todos')

    def test_model_is_set_up_if_invoked(self):
        t = self.Todo()

        self.assertTrue(Todo._set_up)
        self.assertEqual(Todo.table_name, 'todos')

    def test_model_is_set_up_if_chained(self):
        self.Todo.limit(2).get()

        self.assertTrue(self.Todo._set_up)
        self.assertEqual(self.Todo.table_name, 'todos')

    def test_model_is_not_set_up_if_not_invoked(self):
        self.assertFalse(self.Todo._set_up)
        self.assertEqual(self.Todo.table_name, '')

