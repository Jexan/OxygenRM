from . import *

class TestModelGeneration(unittest.TestCase):
    def tearDown(self):
        db.drop_all_tables()

    def setUp(self):
        db.create_table('todos', default_cols(a='text'))

    def test_dumb_model_generation(self):
        Todo = O.generate_model_class('todos')

        self.assertIsInstance(Todo(), O.Model)
        self.assertIsInstance(Todo._fields['a'], Text)

    def test_dumb_model_ops(self):
        Todo = O.generate_model_class('todos')

        Todo.craft(a='hey')
        self.assertEqual(Todo.count(), 1)
        self.assertEqual(Todo.first().a, 'hey')

    def test_smart_model_generation(self):
        todos = Table('todos')
        todos.id = c.Id()
        todos.save()

        Todo = O.generate_model_class('todos')
        self.assertIsInstance(Todo._fields['id'], Id)

        todo = Todo.craft(a='t')
        self.assertEqual(todo.a, 't')
        self.assertEqual(todo.id, 1)

    def test_smart_model_generation_with_custom_id(self):
        todos = Table('todos')
        todos.key = c.Id()
        todos.save()

        Todo = O.generate_model_class('todos', id_name='key')
        self.assertIsInstance(Todo._fields['key'], Id)

        todo = Todo.craft(a='t')
        self.assertEqual(todo.a, 't')
        self.assertEqual(todo.key, 1)