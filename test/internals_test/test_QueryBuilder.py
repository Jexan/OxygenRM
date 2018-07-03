import unittest
from OxygenRM import db_config, internal_db

# FOR NOW
db = db_config('sqlite3', ':memory:')

from OxygenRM.internals.QueryBuilder import *

t1 = QueryBuilder('t')
t2 = QueryBuilder.table('t')

# select all from t
saft = 'SELECT * FROM t'

class TestQueryBuilder(unittest.TestCase):
    def test_initialization(self):
        self.assertIsInstance(t1, QueryBuilder)
        self.assertIsInstance(t2, QueryBuilder)

    def test_table_name_set_ok(self):
        self.assertEqual(t1._in_wait['table_name'], 't')
        self.assertEqual(t2._in_wait['table_name'], 't')

    def test_query_creation(self):
        self.assertEqual(t1.get(), saft)

    def test_select(self):
        t = QueryBuilder.table('t').select('a', 'b')
        self.assertEqual(t.get(), 'SELECT a, b FROM t')

    def test_where(self):
        t = QueryBuilder.table('t').where('a', '=', 2)
        self.assertEqual(t.get(), saft + 'WHERE a = ?')

    def test_or_where(self):
        t = QueryBuilder.table('t').where('a', '=', 2).or_where('b', 'IS', None)
        self.assertEqual(t.get(), saft + 'WHERE a = ? OR b IS ?')

    def test_group_by(self):
        t = QueryBuilder.table('t').group_by('a')
        self.assertEqual(t.get(), saft + 'GROUP BY a ASC')

    def test_having(self):
        t = QueryBuilder.table('t').group_by('a').having('b', '>', 5)
        self.assertEqual(t.get(), saft + 'GROUP BY a ASC HAVING b > 5')

    def test_limit(self):
        t = QueryBuilder.table('t').limit(5)
        self.assertEqual(t.get(), saft + 'LIMIT 5')

    def test_offset(self):
        t = QueryBuilder.table('t').limit(5).offset(4)
        self.assertEqual(t.get(), saft + 'LIMIT 5 OFFSET 4')

    def test_distinct(self):
        t = QueryBuilder.table('t').distinct()
        self.assertEqual(t.get(), 'SELECT DISTINCT * FROM t')

    def test_cross_join(self):
        t = QueryBuilder.table('t').cross_join('s')
        self.assertEqual(t.get(), saft + ' CROSS JOIN s')
        
    def test_natural_join(self):
        t = QueryBuilder.table('t').join('s')
        self.assertEqual(t.get(), saft + ' NATURAL INNER JOIN s')

    def test_natural_outer_join(self):
        t = QueryBuilder.table('t').outer_join('s')
        self.assertEqual(t.get(), saft + ' NATURAL OUTER JOIN s')

    def test_join_using(self):
        t = QueryBuilder.table('t').join('s').using(['a', 'b'])
        self.assertEqual(t.get(), saft + ' INNER JOIN s USING (a, b)')

    def test_outer_join_using(self):
        t = QueryBuilder.table('t').outer_join('s').using(('a', 'b',))
        self.assertEqual(t.get(), saft + ' OUTER JOIN s USING (a, b)')

    def test_join_on(self):
        t = QueryBuilder.table('t').join('s').on('t.a', '=', 's.b')
        self.assertEqual(t.get(), saft + ' INNER JOIN s ON t.a = s.b')

    def test_outer_join_on(self):
        t = QueryBuilder.table('t').outer_join('s').on('t.a', '=', 's.b')
        self.assertEqual(t.get(), saft + ' OUTER JOIN s ON t.a = s.b')

    def test_or_on_join(self):
        t = QueryBuilder.table('t').join('s').on('t.a', '=', 's.b').or_on('t.c', '>', 's.d')
        self.assertEqual(t.get(), saft + ' INNER JOIN s ON t.a = s.b OR t.c > s.d')

    def test_delete_clause(self):
        t = QueryBuilder.table('t')
        self.assertEqual(t.delete(), 'DELETE FROM t')

    def test_delete_clause_where(self):
        t = QueryBuilder.table('t').where('id', '=', 2)
        self.assertEqual(t.delete(), 'DELETE FROM t WHERE id = ?')