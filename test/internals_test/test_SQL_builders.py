import unittest
from OxygenRM.internals.SQL_builders import *
from collections import OrderedDict

_ = True

class TestSQLite3DBHelpers(unittest.TestCase):
    def test_select_clause_without_fields_is_select_all(self):
        expected = 'SELECT * FROM test'
        self.assertEqual(select_clause('test'), expected)

    def test_select_clause_with_fields(self):
        expected = 'SELECT field1, field2, field3 FROM test'
        self.assertEqual(select_clause('test', 'field1', 'field2', 'field3'), expected)

    def test_where_crafs_sql_no_matter_the_last_connector(self):
        expected = 'WHERE f1 = ? AND f2 IS ? OR (f3 NOT NULL AND f3 >= ?)'
        result1 = where_clause((('f1', '=', _, 'AND'), ('f2', 'IS', _, 'OR'), ('f3', '>=', _, 'OR')))
        result2 = where_clause((('f1', '=', _, 'AND'), ('f2', 'IS', _, 'OR'), ('f3', '>=', _, 'AND')))

        self.assertEqual(result1, expected)
        self.assertEqual(result2, expected)

    def test_where_raises_value_error_with_bad_parameters(self):
        self.assertRaises(ValueError, where_clause, (('f1', 'bad', _, 'AND')))
        self.assertRaises(ValueError, where_clause, (('f1', False, _, 'AND')))
        self.assertRaises(ValueError, where_clause, (('f1', '=', _, 'bad')))
        self.assertRaises(ValueError, where_clause, (('f1', '=', _, 1)))

    def test_where_equals_clause_empty_conditions_raises_ValueError(self):
        self.assertRaises(ValueError, where_equals_clause)

    def test_where_equals_clause_ineq_clauses(self):
        expected1 = 'WHERE (id IS NULL OR id != ?) AND (name NOT NULL AND name >= ?)'
        result = where_equals_clause(('id', '!=', 1), ('name', '>=', 1))
        
        self.assertEqual(result[0], expected1)
        self.assertEqual(result[1], (1,1))

    def test_where_equals_clause_eq_to_none_clause(self):
        expected = 'WHERE id IS ?'

        self.assertEqual(where_equals_clause(id=None)[0], expected)

    def test_where_equals_clause_eq_to_none_clause(self):
        expected = 'WHERE id IS ?'
        result = where_equals_clause(id=None)

        self.assertEqual(result[0], expected)
        self.assertEqual(result[1], (None,))

    def test_update_clause_with_one(self):
        expected = "UPDATE test SET a = ?"
        result   = update_clause('test', {'a':1})
        
        self.assertEqual(result, expected)

    def test_update_clause_with_many(self):
        expected = "UPDATE test SET a = ?, b = ?, c = ?"
        result   = update_clause('test', OrderedDict((('a', 1), ('b', 2), ('c', 3))))
        
        self.assertEqual(result, expected)

    def test_update_clause_with_list(self):
        expected = "UPDATE test SET a = ?, b = ?, c = ?"
        result   = update_clause('test', ['a', 'b', 'c'])
        
        self.assertEqual(result, expected)

    def test_create_table_clause(self):
        expected = "CREATE TABLE test (a t1, b t2, c t3)"
        result   = create_table_clause('test', OrderedDict((('a', 't1'), ('b', 't2'), ('c', 't3'))))
        
        self.assertEqual(result, expected)

    def test_drop_table_clause(self):
        expected = "DROP TABLE IF EXISTS test"
        result   = drop_table_clause('test')
        
        self.assertEqual(result, expected)

    def test_equals_clause_with_one(self):
        expected = ('t1', '=', 1, 'AND')

        self.assertEqual(next(equals_conditions(t1=1)), expected)

    def test_equals_clause_with_some(self):
        expected1 = ('t1', '=', 1, 'AND')
        expected2 = ('t2', '=', None, 'AND')
        expected3 = ('t3', '=', 'a', 'AND')

        conditions = equals_conditions(t1=1, t2=None, t3='a')

        self.assertEqual(sorted(list(conditions)), sorted([expected1, expected2, expected3]))

    def test_connect_with(self):
        expected = ('t1', '=', 1, 'AND')

        result = next(connect_with((('t1', '=', 1),), 'AND'))

        self.assertEqual(expected, result)