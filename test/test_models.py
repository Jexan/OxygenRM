# Test cases for OxygenRM Models

import unittest
from OxygenRM import db_config
from .internals_test import default_cols

db = db_config('sqlite3', ':memory:')

import OxygenRM.models as O

db.create_table('todos', default_cols(a='text'))

class ToDo(O.Model):
	pass
		
class TestModels(unittest.TestCase):
	def test_model_initialization(self):
		t = ToDo()

		self.assertIsInstance(t, ToDo)
		self.assertIsInstance(t, O.Model)

	def test_model_is_set_up_if_invoked(self):
		t = ToDo()
		self.assertTrue(ToDo._set_up)
		self.assertIsNot(ToDo._db_fields, None)
		self.assertIsNot(ToDo._Row, None)

		self.assertEqual(ToDo.table_name, 'todos')
		self.assertEqual(ToDo._db_fields, {'a': 'text'})
	
	def test_model_is_not_set_up_if_not_invoked(self):
		db.create_table('users', default_cols(a='text'))
		class User(O.Model):
			pass

		self.assertFalse(User._set_up)
		self.assertIs(User._db_fields, None)
		self.assertIs(User._Row, None)
		self.assertEqual(User.table_name, '')

	def test_model_can_have_custom_table_name(self):
		pass

	def test_models_create_and_new(self):
		pass
		
	def test_models_delete(self):
		pass

	def test_models_destroy(self):
		pass

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