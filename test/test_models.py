# Test cases for OxygenRM Models

import unittest
import OxygenRM.models as O
from OxygenRM import db_config

db_config(driver="sqlite", db="test.db")

class ToDo(O.Model):
	pass
		
class TestModels(unittest.TestCase):
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