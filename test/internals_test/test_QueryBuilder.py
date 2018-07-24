import unittest

from OxygenRM import db
from OxygenRM.internals.QueryBuilder import *
from . import default_cols

t1 = QueryBuilder('t')
t2 = QueryBuilder.table('t')

# select all from t
saft = 'SELECT * FROM t'

# ALIAS

qb = QueryBuilder

class TestQueryBuilderSQL(unittest.TestCase):
    def test_initialization(self):
        self.assertIsInstance(t1, QueryBuilder)
        self.assertIsInstance(t2, QueryBuilder)

    def test_table_name_set_ok(self):
        self.assertEqual(t1._in_wait['table_name'], 't')
        self.assertEqual(t2._in_wait['table_name'], 't')

    def test_query_creation(self):
        self.assertEqual(t1.get_sql(), saft)

    def test_select(self):
        t = QueryBuilder.table('t').select('a', 'b')
        self.assertEqual(t.get_sql(), 'SELECT a, b FROM t')

    def test_where(self):
        t = QueryBuilder.table('t').where('a', '=', 2)
        self.assertEqual(t.get_sql(), saft + ' WHERE a = ?')

    def test_or_where(self):
        t = QueryBuilder.table('t').where('a', '=', 2).or_where('b', 'IS', None)
        self.assertEqual(t.get_sql(), saft + ' WHERE a = ? OR b IS ?')

    def test_where_in(self):
        t = QueryBuilder.table('t').where_in('a', (1,2,3))
        self.assertEqual(t.get_sql(), saft + ' WHERE a IN (?, ?, ?)')

    def test_order_by(self):
        t = QueryBuilder.table('t').order_by('id', 'ASC')
        self.assertEqual(t.get_sql(), saft + ' ORDER BY id ASC')

    def test_group_by(self):
        t = QueryBuilder.table('t').group_by('a')
        self.assertEqual(t.get_sql(), saft + ' GROUP BY a ASC')

    def test_having(self):
        t = QueryBuilder.table('t').group_by('a').having('b', '>', 5)
        self.assertEqual(t.get_sql(), saft + ' GROUP BY a ASC HAVING b > ?')

    def test_limit(self):
        t = QueryBuilder.table('t').limit(5)
        self.assertEqual(t.get_sql(), saft + ' LIMIT 5')

    def test_offset(self):
        t = QueryBuilder.table('t').limit(5).offset(4)
        self.assertEqual(t.get_sql(), saft + ' LIMIT 5 OFFSET 4')

    def test_distinct(self):
        t = QueryBuilder.table('t').distinct()
        self.assertEqual(t.get_sql(), 'SELECT DISTINCT * FROM t')

    def test_cross_join(self):
        t = QueryBuilder.table('t').cross_join('s')
        self.assertEqual(t.get_sql(), saft + ' CROSS JOIN s')
        
    def test_natural_join(self):
        t = QueryBuilder.table('t').join('s')
        self.assertEqual(t.get_sql(), saft + ' NATURAL INNER JOIN s')

    def test_natural_outer_join(self):
        t = QueryBuilder.table('t').outer_join('s')
        self.assertEqual(t.get_sql(), saft + ' NATURAL OUTER JOIN s')

    def test_join_using(self):
        t = QueryBuilder.table('t').join('s').using(['a', 'b'])
        self.assertEqual(t.get_sql(), saft + ' INNER JOIN s USING (a, b)')

    def test_outer_join_using(self):
        t = QueryBuilder.table('t').outer_join('s').using(('a', 'b',))
        self.assertEqual(t.get_sql(), saft + ' OUTER JOIN s USING (a, b)')

    def test_join_on(self):
        t = QueryBuilder.table('t').join('s').on('t.a', '=', 's.b')
        self.assertEqual(t.get_sql(), saft + ' INNER JOIN s ON t.a = s.b')

    def test_outer_join_on(self):
        t = QueryBuilder.table('t').outer_join('s').on('t.a', '=', 's.b')
        self.assertEqual(t.get_sql(), saft + ' OUTER JOIN s ON t.a = s.b')

    def test_or_on_join(self):
        t = QueryBuilder.table('t').join('s').on('t.a', '=', 's.b').or_on('t.c', '>', 's.d')
        self.assertEqual(t.get_sql(), saft + ' INNER JOIN s ON t.a = s.b OR t.c > s.d')

    def test_delete_clause(self):
        t = QueryBuilder.table('t')
        self.assertEqual(t.delete_sql(), 'DELETE FROM t')

    def test_delete_clause_where(self):
        t = QueryBuilder.table('t').where('id', '=', 2)
        self.assertEqual(t.delete_sql(), 'DELETE FROM t WHERE id = ?')

    def test_update_clause(self):
        t = QueryBuilder.table('t')
        self.assertEqual(t.update_sql({'a': None}), 'UPDATE t SET a = ?')

    def test_update_clause_where(self):
        t = QueryBuilder.table('t').where('id', '=', 2)
        self.assertEqual(t.update_sql({'a': None}), 'UPDATE t SET a = ? WHERE id = ?')



class RecordManipulationTest(unittest.TestCase):
    def tearDown(self):
        db.drop_table('t')

    def test_table_querying_all(self):
        db.create_table('t', default_cols(name='text', number='integer'))
        db.create('t', name='t1', number=1)
        
        created = next(qb.table('t').all())
        self.assertEqual(created['name'], 't1')
        self.assertEqual(created['number'], 1)

    def test_table_first(self):
        db.create_table('t', default_cols(a='text', b='integer'))
        db.create_many('t', ('a', 'b'), (('t1', 1), ('t2', 2)))

        first = qb.table('t').first()

        self.assertEqual(first['a'], 't1')
        self.assertEqual(first['b'], 1)

    # FIND WHERE GET
    def test_where_inequality_works_even_with_null_records(self):
        db.create_table('t', default_cols(a='integer', b='text'))
        db.create_many('t', ('a', 'b'), ((1,'t1'), (2, 't2'), (3, None), (None, 't4')))
    
        fields_with_a_not_3 = list(qb.table('t').where('a', '!=', 3))

        # Without the 'NOT NULL' added in the method, this would not count the record with the name t6
        self.assertEqual(len(fields_with_a_not_3), 3)

        for field in fields_with_a_not_3:
            self.assertFalse(field['a'] == 3) 

    def test_find_where_lte_works(self):
        db.create_table('t', default_cols(a='integer', name='text'))
        db.create_many('t', ('a', 'name'), [(1,'t1'), (2, 't2'), (3, None), (None, 't3'), (5, 't4')])
    
        field_with_a_le_than_3 = list(qb.table('t').where_many([('a', '<=', 3)]))
        
        self.assertEqual(len(field_with_a_le_than_3), 3)

        for row in field_with_a_le_than_3:
            self.assertTrue(row['a'] <= 3)
            self.assertIn(row['name'], ['t1', 't2', None])
    
    def test_where_gt_works(self):
        db.create_table('t', default_cols(a='integer', b='text'))
        db.create_many('t', ('a', 'b'), [(1,'t1'), (2, 't2'), (3, None), (None, 't3'), (5, 't4')])
    
        field_with_a_gt_2 = list(qb.table('t').where('a', '>', 2))
        
        self.assertEqual(len(field_with_a_gt_2), 2)

        for row in field_with_a_gt_2:
            self.assertTrue(row['a'] > 2)
            self.assertIn(row['b'], ['t4', None])

    def test_where_many_with_two_conditions(self):
        db.create_table('t', default_cols(a='integer', b='text', c='real'))

        db.create('t', a=1, b='t1', c=3.4)
        db.create('t', a=2, b='t2', c=.3)
        db.create('t', a=3)
        db.create('t', b='t4')

        field_with_two_cond = list(qb.table('t').where_many([('a', '!=', 3), ('c', '>=', 1)]))
        self.assertEqual(len(field_with_two_cond), 1)
        self.assertEqual(field_with_two_cond[0]['b'], 't1')

    def test_where_in(self):
        db.create_table('t', default_cols(a='integer', b='text'))
        db.create_many('t', ('a', 'b'), [(1, '1'), (2, '2'), (3, '3'), (4, '4')])

        even_fields = tuple(qb.table('t').where_in('a', (2, 3)))
        
        self.assertEqual(len(even_fields), 2)
        self.assertEqual(even_fields[0]['b'], '2')

    def test_where_equals_works(self):
        db.create_table('t', default_cols(id='integer', name='text'))

        db.create('t', id=1, name='t1')
        db.create('t', id=2, name='t2')
        db.create('t', id=3)

        query = qb.table('t').where('id', '=', 1)
        field_with_id_1 = list(qb.table('t').where('id', '=', 1))

        self.assertEqual(len(field_with_id_1), 1)
        self.assertEqual(field_with_id_1[0]['name'], 't1')

    def test_where_equality_to_non_null_value_doesnt_count_nulls(self):
        db.create_table('t', default_cols(a='integer', b='integer'))
        db.create_many('t', ('a', 'b'), ((None, 1), (2, 2)))

        field_with_id_2 = list(qb.table('t').where('a', '=', 2))
        self.assertEqual(len(field_with_id_2), 1)
        self.assertEqual(field_with_id_2[0]['b'], 2)

    def test_find_equals_equality_to_null_finds_nulls(self):
        db.create_table('t', default_cols(a='integer', b='text'))
        db.create('t', b='t1')

        field_with_null_val = list(qb.table('t').where('a', '=', None))
        self.assertEqual(field_with_null_val[0]['a'], None)
        self.assertEqual(field_with_null_val[0]['b'], 't1')

    def test_db_deletion_equality(self):
        db.create_table('t', default_cols(id='integer', name='text'))

        db.create('t', id=1, name='t1')
        db.create('t', name='t2')

        self.assertEqual(len(list(qb.table('t'))), 2)

        qb.table('t').where('name', '=', 't1').delete()
        rows = list(qb.table('t'))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['name'], 't2')

    def test_db_deletion_null(self):
        db.create_table('t', default_cols(id='integer', name='text'))
        db.create('t', name='t1')
        db.create('t', id=4, name='t5')
        db.create('t', id=2, name='t2')
        db.create('t', id=3)
        db.create('t', name='t4')

        qb.table('t').where('id', '=', None).delete()

        rows = list(qb.table('t'))
        self.assertEqual(len(rows), 3)
        for row in rows:
            self.assertNotEqual(row['id'], None)

    def test_db_update_equal_works(self):
        db.create_table('t', default_cols(id='integer'))
        db.create('t', id=1)
        
        qb.table('t').where('id', '=', 1).update({'id':2})
        
        self.assertEqual(next(db.all('t'))['id'], 2)

    def test_db_update_doesnt_update_not_found_columns(self):
        db.create_table('t', default_cols(id='integer'))
        db.create('t', id=0)
        qb.table('t').where('id', '=', '1').update({'id':2})

        self.assertEqual(next(db.all('t'))['id'], 0)

    def test_db_update_a_lot_of_cols(self):
        db.create_table('t', default_cols(id='integer', number='integer'))
        db.create_many('t', ('id', 'number'), ((1, i) for i in range(10)))
        for row in db.all('t'):
            self.assertNotEqual(row['number'], -1)

        qb.table('t').where('id', '=', 1).update({'number':-1})
        for row in db.all('t'):
            self.assertEqual(row['number'], -1)

    def test_update_all(self):
        db.create_table('t', default_cols(id='integer'))
        db.create_many('t', ('id',), ((1,) for _ in range(10)))

        qb.table('t').update({'id':0})
        for row in db.all('t'):
            self.assertEqual(row['id'], 0)