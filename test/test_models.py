# Test cases for OxygenRM Models

import unittest
from OxygenRM import internal_db as db
from OxygenRM.internals.fields import *
from .internals_test import default_cols

import OxygenRM.models as O

class Todo(O.Model):
    pass

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
        t = Todo()

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
            pass

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
        print(t.a)

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

    def test_models_destroy(self):
        create_todo()

        t = Todo.where('a', '=', 't').first()
        t.destroy()

        record = db.all('todos').fetchone()
        self.assertIs(record, None)

    def test_models_delete(self):
        create_todo()

        t = Todo.where('a', '=', 't').delete()

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

    def test_models_fetching_all(self):
        pass

    def test_models_fetching_specific(self):
        pass

    def test_models_where_clauses(self):
        pass

    def test_models_first_and_last(self):
        pass

    def test_models_ordering(self):
        pass

    def test_models_converting_to_data(self):
        pass

    def test_to_formats(self):
        pass

    def test_get_dict(self):
        pass

def create_todo():
    db.create('todos', a='t')