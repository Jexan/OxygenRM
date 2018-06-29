import unittest
from OxygenRM.internals.SQL_builders import *
from collections import OrderedDict

class TestSQLite3DBHelpers(unittest.TestCase):
    def test_select_clause_without_fields_is_select_all(self):
        expected = 'SELECT * FROM test'
        self.assertEqual(select_clause('test'), expected)

    def test_select_clause_with_fields(self):
        expected = 'SELECT field1, field2, field3 FROM test'
        self.assertEqual(select_clause('test', 'field1', 'field2', 'field3'), expected)

    def test_where_clause_empty_conditions_raises_ValueError(self):
        self.assertRaises(ValueError, where_clause)

    def test_where_clause_ineq_clauses(self):
        expected1 = 'WHERE (id IS NULL OR id != ?) AND (name NOT NULL AND name >= ?)'
        result = where_clause(('id', '!=', 1), ('name', '>=', 1))
        self.assertEqual(result[0], expected1)
        self.assertEqual(result[1], (1,1))

    def test_where_clause_eq_to_none_clause(self):
        expected = 'WHERE id IS ?'
        self.assertEqual(where_clause(id=None)[0], expected)

    def test_where_clause_eq_to_none_clause(self):
        expected = 'WHERE id IS ?'
        result = where_clause(id=None)
        self.assertEqual(result[0], expected)
        self.assertEqual(result[1], (None,))

    def test_update_clause_with_one(self):
        expected = "UPDATE test SET a = ?"
        result   = update_clause('test', {'a':1})
        
        self.assertEqual(result.query, expected)
        self.assertEqual(result.args, (1,))

    def test_update_clause_with_many(self):
        expected = "UPDATE test SET a = ?, b = ?, c = ?"
        result   = update_clause('test', OrderedDict((('a', 1), ('b', 2), ('c', 3))))
        
        self.assertEqual(result.query, expected)
        self.assertEqual(result.args, (1,2,3))

    def test_create_table_clause(self):
        expected = "CREATE TABLE test (a t1, b t2, c t3)"
        result   = create_table_clause('test', OrderedDict((('a', 't1'), ('b', 't2'), ('c', 't3'))))
        
        self.assertEqual(result, expected)

    def test_drop_table_clause(self):
        expected = "DROP TABLE IF EXISTS test"
        result   = drop_table_clause('test')
        
        self.assertEqual(result, expected)
