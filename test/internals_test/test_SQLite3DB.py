# Test cases for OxygenRM Models

import unittest
import os
import logging

logging.basicConfig(filename='test/test.log',level=logging.DEBUG)

import sqlite3 as sql3
from OxygenRM.internals.SQLite3DB import *

db_name = 'test/test.db'
os.unlink(db_name)
db = SQLite3DB(db_name)
conn = db.connection

def drop_table(table):
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS ' + table)
    conn.commit()

def create_table(table, **cols):
    c = conn.cursor()
    c.execute('CREATE TABLE ' + table + ' (' + cols['name'] + ' ' + cols['type'] + ')')
    conn.commit()

class TestSQLite3DB(unittest.TestCase):
    def tearDown(self):
        db.drop_all_tables()

    def test_db_initializes_connection(self):
        self.assertIsInstance(conn, sql3.Connection)
    
    def test_table_cols_info_queries_info_correctly(self):
        create_table('test', name= 'name', type='text')
        info = list(db.table_cols_info('test'))

        self.assertEqual(len(info), 1)

        # Check if the info dict is correct.
        self.assertEqual(info[0]['name'], 'name')
        self.assertEqual(info[0]['type'], 'text')
        self.assertEqual(info[0]['cid'], 0)

    def test_table_creation_creates_table_and_cols(self):
        db.create_table('test', name='text', age='integer')
        info = list(db.table_cols_info('test'))

        # Since dicts are not ordered.
        if info[0]['name'] == 'name':
            name_col = info[0]
            age_col  = info[1]
        else: 
            name_col = info[1]
            age_col  = info[0]
 
        self.assertEqual(len(info), 2)

    def test_table_creation_raises_typeerror_if_type_is_unvalid(self):
        self.assertRaises(TypeError, db.create_table, 't', name='nonsense', age='what')
        self.assertRaises(TypeError, db.create_table, 't', name=True, age=2)
        self.assertRaises(TypeError, db.create_table, 't', name=1.j, t=complex)

    def test_table_fields_types_returns_every_field_with_his_type(self):
        db.create_table('test', name='text', 
            float='real', blob='blob', number='integer')

        info = db.table_fields_types('test')

        self.assertEqual(info['name'], 'text') 
        self.assertEqual(info['float'], 'real') 
        self.assertEqual(info['blob'], 'blob') 
        self.assertEqual(info['number'], 'integer') 

    def test_get_database_tables_lists_every_table(self):
        db.create_table('test', name='text')
        db.create_table('test2', float='real')

        info = list(db.get_all_tables())

        self.assertEqual(len(info), 2)
        self.assertIn('test', info)
        self.assertIn('test2', info)
    
    def test_table_existence_detects_whether_a_table_exists(self):
        self.assertFalse(db.table_exists('test'))

        db.create_table('test', name='text')

        self.assertTrue(db.table_exists('test'))

    def test_table_drop(self):
        self.assertEqual(len(list(db.get_all_tables())), 0)
        db.create_table('test', t='text')

        self.assertEqual(len(list(db.get_all_tables())), 1)

        db.drop_table('test')
        self.assertEqual(len(list(db.get_all_tables())), 0)

    def test_drop_all_tables_drops_every_table(self):
        self.assertEqual(len(list(db.get_all_tables())), 0)
        db.create_table('test1', t='text')
        db.create_table('test2', t='text')
        db.create_table('test3', t='text')
        db.create_table('test4', t='text')
        db.create_table('test5', t='text')
        db.create_table('test6', t='text')

        self.assertEqual(len(list(db.get_all_tables())), 6)

        db.drop_all_tables()

        self.assertEqual(len(list(db.get_all_tables())), 0)

    def test_record_creation_creates_the_records_correctly(self):
        db.create_table('test', name='text', number='integer')
        
        db.create('test', name='t1', number=1)
        db.create('test', name='t2', number=1)
        db.create('test', number=1)
        db.create('test', name='t4')

        c = conn.cursor()

        for row in c.execute('SELECT name, number FROM test'):
            self.assertIn(row['name'], ['t1', 't2', 't4', None])
            self.assertIn(row['number'], [1, None])
            
    def test_table_querying_all(self):
        db.create_table('test', name='text', number='integer')

        self.assertEqual(len(list(db.all('test'))), 0)
        
        db.create('test', name='t1', number=1)
        self.assertEqual(len(list(db.all('test'))), 1)

        created = db.all('test').fetchone()
        self.assertEqual(created['name'], 't1')
        self.assertEqual(created['number'], 1)

    def test_table_where_finds_item(self):
        db.create_table('test', id="integer", name="text")

        db.create('test', id=1, name='t1')
        db.create('test', id=2, name='t2')
        db.create('test', id=3)
        db.create('test', id=5, name="t4")
        db.create('test', id=4, name="t5")
        db.create('test', name="t6")

        field_with_id_1 = list(db.find_where('test', id=1))
        self.assertEqual(len(field_with_id_1), 1)
        self.assertEqual(field_with_id_1[0]['name'], 't1')

        field_with_id_le_than_3 = list(db.find_where('test', ('id', '<=', 3)))
        self.assertEqual(len(field_with_id_le_than_3), 3)
        for row in field_with_id_le_than_3:
            self.assertTrue(row['id'] <= 3)
            self.assertIn(row['name'], ['t1', 't2', None])


        fields_with_id_not_3 = list(db.find_where('test', ('id', '!=', 3)))
        # Without the "NOT NULL" added in the method, this would not count the record with the name t6
        self.assertEqual(len(fields_with_id_not_3), 5)

        field_with_null_val = list(db.find_where('test', id=None))
        self.assertEqual(field_with_null_val[0]['id'], None)
        self.assertEqual(field_with_null_val[0]['name'], 't6')

    def test_db_updating(self):
        pass

    def test_db_deletion(self):
        pass

    def test_int_search(self):
        pass