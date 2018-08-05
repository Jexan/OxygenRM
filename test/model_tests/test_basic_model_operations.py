from . import *

class Todo(O.Model):
    a = Text()

Todo.set_up()

def todoWithId():
    db.drop_table('todos')
    db.create_table('todos', 
        (next(default_cols(a='text')), next(default_cols(id='integer'))._replace(primary=True, auto_increment=True))
    )

    class Todo(O.Model):
        a = Text()
        id = Id()

    return Todo

def create_todo():
    db.create('todos', a='t')

class TestModels(unittest.TestCase):
    def tearDown(self):
        db.drop_all_tables()

    def setUp(self):
        db.create_table('todos', default_cols(a='text'))

    def test_model_initialization(self):
        t = Todo()

        self.assertIsInstance(t, Todo)
        self.assertIsInstance(t, O.Model)

    def test_model_field_set_up_correctly(self):
        db.create_table('tests', default_cols(a='text'))
        class Test(O.Model):
            a = Text()

        t = Test()
        t.a = 'hey'
        self.assertEqual(t.a, 'hey')

        with self.assertRaises(TypeError):
            t.a = 12

    def test_model_is_set_up_if_invoked(self):
        t = Todo()
        self.assertTrue(Todo._set_up)

        self.assertEqual(Todo.table_name, 'todos')

    def test_model_is_set_up_if_chained(self):
        db.create_table('users', default_cols(a='text'))
        class User(O.Model):
            a = Text()

        User.limit(2).get()

        self.assertTrue(User._set_up)
        self.assertEqual(User.table_name, 'users')

    def test_model_is_not_set_up_if_not_invoked(self):
        db.create_table('users', default_cols(a='text'))
        class User(O.Model):
            a = Text

        self.assertFalse(User._set_up)
        self.assertEqual(User.table_name, '')

    def test_model_can_have_custom_table_name(self):
        db.create_table('murder', default_cols(name='text'))
        class Crow(O.Model):
            table_name = 'murder'

            name = Text()

        Crow()

        self.assertEqual(Crow.table_name, 'murder')

    def test_model_where_queries(self):
        create_todo()

        t = Todo.where('a', '=', 't').get().first()

        record = db.all('todos').fetchone()
        self.assertEqual(t.a, record['a'])

    def test_multiple_models_dont_get_screwed_up(self):
        create_todo()
        create_todo()

        t = Todo.all().first()
        t.a = 's'

        e = Todo.all()[1]
        e.a = 't'

        self.assertNotEqual(t.a, e.a)

    def test_weird(self):
        class R:
            pass

        R.e = Integer()
        a = R()
        b = R()

        a.e = 1
        b.e = 3

        self.assertNotEqual(a, b)

    def test_model_limit(self):
        for i in range(100):
            create_todo()

        exists = db.table_exists('todos')
        first_50_todos = list(Todo.limit(50).get())

        self.assertEqual(len(first_50_todos), 50)

    def test_models_new(self):
        t = Todo()
        t.a = 't'

        self.assertEqual(t.a, 't')

        t.save()

        record = db.all('todos').fetchone()
        self.assertEqual(record['a'], 't')

        s = Todo()
        t.a = 't2'

        self.assertEqual(t.a, 't2')
        t.save()

        record = list(db.all('todos'))[-1]
        self.assertEqual(record['a'], 't2')

    def test_model_craft_with_id_model(self):
        Todo = todoWithId()

        t = Todo.craft(a='t')
        self.assertEqual(t.a, 't')
        
        record = db.all('todos').fetchone()
        self.assertEqual(record['a'], 't')
    
    def test_model_craft_with_no_model_return_true(self):
        t = Todo.craft(False, a='t')
        self.assertTrue(t)
        
        record = db.all('todos').fetchone()
        self.assertEqual(record['a'], 't')

    def test_models_craft_with_model_with_no_primary_key_returns_no_model(self):
        self.assertTrue(Todo.craft(a='t'))

    def test_models_delete(self):
        create_todo()

        t = Todo.where('a', '=', 't').first()
        t.delete()

        record = db.all('todos').fetchone()
        self.assertIs(record, None)

    def test_models_delete(self):
        create_todo()

        t = Todo.where('a', '=', 't').delete()

        record = db.all('todos').fetchone()
        self.assertIs(record, None)

    def test_models_destroy(self):
        Todo = todoWithId()
        create_todo()

        Todo.destroy(1)

        record = db.all('todos').fetchone()
        self.assertIs(record, None)

    def test_models_table_truncate(self):
        db.create_many('todos', ('a',), ((str(i),) for i in range(10)))
        Todo.truncate()

        record = db.all('todos').fetchone()
        self.assertIs(record, None)

    def test_model_update(self):
        create_todo()

        t = Todo.where('a', '=', 't').first()

        t.a = 's'
        t.save()

        all_records = list(db.all('todos'))
        self.assertEqual(len(all_records), 1)

        record = all_records[0]

        self.assertEqual(record['a'], 's')
