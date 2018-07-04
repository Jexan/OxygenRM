import unittest
import re
from collections import OrderedDict

from OxygenRM.internals.SQL_builders import *
from . import default_cols

_ = True

class TestSQLite3DBHelpers(unittest.TestCase):
    def test_select_clause_without_fields_is_select_all(self):
        expected = 'SELECT * FROM test'
        self.assertEqual(select_clause('test'), expected)

    def test_select_clause_with_fields(self):
        expected = 'SELECT field1, field2, field3 FROM test'
        self.assertEqual(select_clause('test', 'field1', 'field2', 'field3'), expected)

    def test_where_crafs_sql_no_matter_the_first_connector(self):
        expected = 'WHERE f1 = ? OR f2 IS ? AND (f3 NOT NULL AND f3 >= ?)'

        cond1_and = ConditionClause('AND', 'f1', '=', _) 
        cond1_or = ConditionClause('OR', 'f1', '=', _) 
        cond2 = ConditionClause('OR', 'f2', 'IS', _)
        cond3 = ConditionClause('AND', 'f3', '>=', _)

        result1 = where_clause((cond1_and, cond2, cond3))
        result2 = where_clause((cond1_or, cond2, cond3))

        self.assertEqual(result1, expected)
        self.assertEqual(result2, expected)

    def test_where_raises_value_error_with_bad_parameters(self):
        self.assertRaises(ValueError, where_clause, (ConditionClause('AND', 'f1', 'bad', _),))
        self.assertRaises(ValueError, where_clause, (ConditionClause('AND', 'f1', False, _),))
        self.assertRaises(ValueError, where_clause, (ConditionClause('bad', 'f1', '=', _),))
        self.assertRaises(ValueError, where_clause, (ConditionClause(1, 'f1', '=', _),))

    def test_where_equals_clause_empty_conditions_raises_ValueError(self):
        self.assertRaises(ValueError, where_clause, [])

    def test_where_clause_ineq_clauses(self):
        expected1 = 'WHERE (id IS NULL OR id != ?) OR (name NOT NULL AND name >= ?)'
        result = where_clause([ConditionClause('AND', 'id', '!=', 1), ConditionClause('OR', 'name', '>=', 1)])
        
        self.assertEqual(result, expected1)

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
        result   = create_table_clause('test', default_cols(a='t1', b='t2', c='t3'))
        self.assertTrue(re.match("CREATE TABLE test [(]( ?(a|b|c) t(1|2|3),?)+[)]", result))

    def test_simple_column_gen(self):
        expected = 'a integer'
        self.assertEqual(column_gen(default_cols(a='integer')), expected)

    def test_create_complex_column_gen(self):
        expected = 'a text NOT NULL DEFAULT \'JEX\' UNIQUE CHECK(a LIKE "asd_"), id integer PRIMARY KEY AUTOINCREMENT'
        a_col = next(default_cols(a='text'))._replace(null=False, default='JEX', unique=True, check='a LIKE "asd_"')
        id_col = next(default_cols(id='integer'))._replace(primary=True, auto_increment=True)

        result = column_gen((a_col, id_col))

        self.assertEqual(expected, result)

    def test_drop_table_clause(self):
        expected = "DROP TABLE IF EXISTS test"
        result   = drop_table_clause('test')
        
        self.assertEqual(result, expected)

    def test_natural_join_outer_inner(self):
        expected_inner = 'a NATURAL INNER JOIN b'
        expected_outer = 'a NATURAL OUTER JOIN b'

        self.assertEqual(join_clause('INNER', 'a', 'b'), expected_inner)
        self.assertEqual(join_clause('OUTER', 'a', 'b'), expected_outer)

    def test_join_using_clause(self):
        expected = 'a INNER JOIN b USING (i, j, k)'
        cols = ('i', 'j', 'k')

        self.assertEqual(join_clause('INNER', 'a', 'b', using=cols), expected)

    def test_join_on_clause(self):
        expected = 'a INNER JOIN b ON a.a = b.a'
        condition = ConditionClause('AND', 'a.a', '=', 'b.a')

        self.assertEqual(join_clause('INNER', 'a', 'b', on=(condition,)), expected)

    def test_delete_clause(self):
        self.assertEqual(delete_clause('t'), 'DELETE FROM t')

    def test_delete_clause_where(self):
        self.assertEqual(delete_clause('t', (ConditionClause('AND', 'id', '=', 2),)), 'DELETE FROM t WHERE id = ?')

    def test_rename_table_clause(self):
        self.assertEqual(rename_table_clause('t', 's'), 'ALTER TABLE t RENAME TO s')

    def test_add_col_clause(self):
        self.assertEqual(add_column_clause('t', next(default_cols(a='integer'))), 'ALTER TABLE t ADD COLUMN a integer')

    def test_build_columns_from_sql(self):
        sql = '(a text, b integer NOT NULL, c real PRIMARY KEY AUTOINCREMENT)'

        columns = build_columns_from_sql(sql)

        self.assertEqual(column_gen(columns), sql[1:-1])

    def test_build_columns_from_sql_defaults_correctly(self):
        sql = 'CREATE TABLE t (a integer DEFAULT 4000, b text CHECK(b > 4))'
        
        self.assertEqual(column_gen(build_columns_from_sql(sql)), sql[sql.find('(')+1:-1])
