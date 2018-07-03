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

