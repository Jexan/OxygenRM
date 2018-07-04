# Test cases for OxygenRM Models

import unittest
import logging
from . import default_cols

logging.basicConfig(filename='test/test.log',level=logging.DEBUG)

import sqlite3 as sql3
from OxygenRM.internals.SQLite3DB import *
from OxygenRM.internals.columns import ColumnData

db_name = ':memory:'
db = SQLite3DB(db_name)
conn = db.connection

def drop_table(table):
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS ' + table)
    conn.commit()

class TestSQLite3DB(unittest.TestCase):
    def tearDown(self):
        db.drop_all_tables()

    def test_db_initializes_connection(self):
        self.assertIsInstance(conn, sql3.Connection)

    # CREATE TABLE ---------------------------------
    def test_table_creation_creates_table_and_cols(self):
        db.create_table('test', default_cols(name='text', age='integer'))
        info = list(db.table_cols_info('test'))
        # Since dicts are not ordered.
        if info[0]['name'] == 'name':
            name_col = info[0]
            age_col  = info[1]
        else: 
            name_col = info[1]
            age_col  = info[0]
 
        self.assertEqual(len(info), 2)

    def test_complex_table_creation(self):
        column_with_not_null = next(default_cols(a='text'))._replace(null=False)
        column_with_weird_default = next(default_cols(b='text'))._replace(default="' ; \\ \"")
        column_with_check = next(default_cols(c='text'))._replace(check="c > 5")

        db.create_table('t', (column_with_not_null, column_with_weird_default, column_with_check))
        info = list(db.table_cols_info('t'))

        self.assertTrue(info[0]['notnull'])
        self.assertEqual(info[1]['dflt_value'], "''' ; \\ \"'")

    def test_table_creation_raises_typeerror_if_type_is_unvalid(self):
        self.assertRaises(TypeError, db.create_table, 't', default_cols(name='nonsense', age='what'))
        self.assertRaises(TypeError, db.create_table, 't', default_cols(name=True, age=2))
        self.assertRaises(TypeError, db.create_table, 't', default_cols(name=1.j, t=complex))

    def test_table_creation_raises_valueError_if_no_col_is_passed(self):
        self.assertRaises(ValueError, db.create_table, 't', [])

    # TABLE ALTER ------------------------------
    def test_table_renaming(self):
        db.create_table('t', default_cols(a='text'))

        db.rename_table('t', 's')

        self.assertFalse(db.table_exists('t'))
        self.assertTrue(db.table_exists('s'))

    def test_table_add_col(self):
        db.create_table('t', default_cols(a='text'))

        db.add_column('t', next(default_cols(b= 'integer')))

        self.assertEqual(db.table_fields_types('t')['b'], 'integer')

    # Table info ---------------------------------
    def test_table_fields_types_returns_every_field_with_his_type(self):
        db.create_table('test', default_cols(name='text', 
            float='real', blob='blob', number='integer'))

        info = db.table_fields_types('test')

        self.assertEqual(info['name'], 'text') 
        self.assertEqual(info['float'], 'real') 
        self.assertEqual(info['blob'], 'blob') 
        self.assertEqual(info['number'], 'integer') 

    def test_get_database_tables_lists_every_table(self):
        db.create_table('test', default_cols(name='text'))
        db.create_table('test2', default_cols(float='real'))

        info = list(db.get_all_tables())

        self.assertEqual(len(info), 2)
        self.assertIn('test', info)
        self.assertIn('test2', info)
    
    def test_table_existence_detects_whether_a_table_exists(self):
        self.assertFalse(db.table_exists('test'))

        db.create_table('test', default_cols(name='text'))

        self.assertTrue(db.table_exists('test'))

    def test_table_cols_info_queries_info_correctly(self):
        db.create_table('test', default_cols(name= 'text'))
        info = list(db.table_cols_info('test'))

        self.assertEqual(len(info), 1)

        # Check if the info dict is correct.
        self.assertEqual(info[0]['name'], 'name')
        self.assertEqual(info[0]['type'], 'text')
        self.assertEqual(info[0]['cid'], 0)

    def test_get_all_columns(self):
        col = next(default_cols(a='text'))._replace(null=False, default='Testing')
        db.create_table('t', (col,))

        print(col)
        print(next(db.get_all_columns('t')))
        self.assertEqual(next(db.get_all_columns('t')), col)

    # Table Droppage ---------------------------------
    def test_table_drop(self):
        self.assertEqual(len(list(db.get_all_tables())), 0)
        db.create_table('test', default_cols(t='text'))

        self.assertEqual(len(list(db.get_all_tables())), 1)

        db.drop_table('test')
        self.assertEqual(len(list(db.get_all_tables())), 0)

    def test_drop_all_tables_drops_every_table(self):
        self.assertEqual(len(list(db.get_all_tables())), 0)
        db.create_table('test1', default_cols(t='text'))
        db.create_table('test2', default_cols(t='text'))
        db.create_table('test3', default_cols(t='text'))
        db.create_table('test4', default_cols(t='text'))
        db.create_table('test5', default_cols(t='text'))
        db.create_table('test6', default_cols(t='text'))

        self.assertEqual(len(list(db.get_all_tables())), 6)

        db.drop_all_tables()

        self.assertEqual(len(list(db.get_all_tables())), 0)

    # RECORD CREATION ---------------------------------
    def test_record_creation_creates_the_records_correctly(self):
        db.create_table('test', default_cols(name='text', number='integer'))
        
        db.create('test', name='t1', number=1)
        db.create('test', name='t2', number=1)
        db.create('test', number=1)
        db.create('test', name='t4')

        c = conn.cursor()

        for row in c.execute('SELECT name, number FROM test'):
            self.assertIn(row['name'], ['t1', 't2', 't4', None])
            self.assertIn(row['number'], [1, None])
    
    def test_create_many_creates_the_records_correctly(self):
        db.create_table('test', default_cols(name='text', number='integer')       ) 
        db.create_many('test', ('number', 'name'), [(1,'t1'), (None, 't2'), (3, None)])

        c = conn.cursor()

        for row in c.execute('SELECT name, number FROM test'):
            self.assertIn(row['name'], ['t1', 't2', None])
            self.assertIn(row['number'], [1, 3, None])
            
    def test_table_querying_all(self):
        db.create_table('test', default_cols(name='text', number='integer'))

        self.assertEqual(len(list(db.all('test'))), 0)
        
        db.create('test', name='t1', number=1)
        self.assertEqual(len(list(db.all('test'))), 1)

        created = db.all('test').fetchone()
        self.assertEqual(created['name'], 't1')
        self.assertEqual(created['number'], 1)