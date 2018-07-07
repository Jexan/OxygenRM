# Test cases for OxygenRM Models

import unittest
from OxygenRM import db_config
from .internals_test import default_cols

db = db_config('sqlite3', ':memory:')

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

    def test_model_is_set_up_if_invoked(self):
        t = Todo()
        self.assertTrue(Todo._set_up)
        self.assertIsNot(Todo._db_fields, None)
        self.assertIsNot(Todo._Row, None)

        self.assertEqual(Todo.table_name, 'todos')
        self.assertEqual(Todo._db_fields, {'a': 'text'})

    def test_model_is_set_up_if_chained(self):
        db.create_table('users', default_cols(a='text'))
        class User(O.Model):
            pass

        User.limit(2)

        self.assertTrue(User._set_up)
        self.assertIsNot(User._db_fields, None)
        self.assertIsNot(User._Row, None)
        self.assertEqual(User.table_name, 'users')

    def test_model_is_not_set_up_if_not_invoked(self):
        db.create_table('users', default_cols(a='text'))
        class User(O.Model):
            pass

        self.assertFalse(User._set_up)
        self.assertIs(User._db_fields, None)
        self.assertIs(User._Row, None)
        self.assertEqual(User.table_name, '')

    def test_model_can_have_custom_table_name(self):
        db.create_table('murder', default_cols(name='text'))
        class Crow(O.Model):
            table_name = 'murder'

        Crow()

        self.assertEqual(Crow.table_name, 'murder')
        self.assertEqual(Crow._db_fields['name'], 'text')

    def test_model_where_queries(self):
        create_todo()

        t = next(Todo.where('a', '=', 't').get())

        record = db.all('todos').fetchone()
        self.assertEqual(t.a, record['a'])

    def test_model_limit(self):
        for i in range(100):
            create_todo()

        first_50_todos = list(Todo.limit(50).get())

        self.assertEqual(len(first_50_todos), 50)

    def test_models_new(self):
        t = Todo()
        t.a = 't'

        self.assertEqual(t.a, 't')

        t.save()

        record = db.all('todos').fetchone()
        self.assertEqual(record['a'], 't')

    def test_models_delete(self):
        create_todo()

        t = Todo.where('a', '=', 't').get()
        t.delete()

        record = db.all('todos').fetchone()
        self.assertNone(record)

    def test_models_destroy(self):
        create_todo()

        t = Todo.destroy(a='t')

        record = db.all('todos').fetchone()
        self.assertNone(record)

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

    def test_where_string_pattern(self):
        pass

    def test_where_array_pattern(self):
        pass

    def test_where_kwargs_pattern(self):
        pass

    def test_where_dict_pattern(self):
        pass

    def test_last(self):
        pass

    def test_getting_correct_table_prop(self):
        pass

    def test_to_formats(self):
        pass

    def test_get_dict(self):
        pass

def create_todo():
    db.create('todos', a='t')