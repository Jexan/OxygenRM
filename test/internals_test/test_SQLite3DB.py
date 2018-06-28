# Test cases for OxygenRM Models

import unittest
import os

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
        drop_table('test')

    def test_db_initializes(self):
        self.assertIsInstance(conn, sql3.Connection)
    
    def test_table_cols_info(self):
        create_table('test', name= 'name', type='text')
        info = list(db.table_cols_info('test'))

        self.assertEqual(len(info), 1)

        # Check if the info dict is correct.
        self.assertEqual(info[0]['name'], 'name')
        self.assertEqual(info[0]['type'], 'text')
        self.assertEqual(info[0]['cid'], 0)

    def test_table_creation(self):
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

        self.assertEqual(name_col['name'], 'name')
        self.assertEqual(age_col['name'], 'age')

        self.assertEqual(name_col['type'], 'text')
        self.assertEqual(age_col['type'], 'integer')

        drop_table('test')

    def test_table_fields_types(self):
        db.create_table('test', name='text', 
            float='real', blob='blob', number="integer")

        info = db.table_fields_types('test')

        self.assertEqual(info['name'], 'text') 
        self.assertEqual(info['float'], 'real') 
        self.assertEqual(info['blob'], 'blob') 
        self.assertEqual(info['number'], 'integer') 

    def test_get_database_tables(self):
        db.create_table('test', name="text")
        db.create_table('test2', float='real')

        info = list(db.get_all_tables())

        self.assertEqual(len(info), 2)
        self.assertIn('test', info)
        self.assertIn('test2', info)

        drop_table('test2')

    def test_record_creation(self):
        db.create_table('test', name="text", number="integer")
        
        db.create('test', name="t1", number=1)
        db.create('test', name="t2", number=1)
        db.create('test', number=1)
        db.create('test', name="t4")

        c = conn.cursor()

        for row in c.execute('SELECT name, number FROM test'):
            self.assertIn(row['name'], ['t1', 't2', 't4', None])
            self.assertIn(row['number'], [1, None])
            
    def test_table_querying_all(self):
        db.create_table('test', name="text", number="integer")

        self.assertEqual(len(list(db.all('test'))), 0)
        
        db.create('test', name="t1", number=1)
        self.assertEqual(len(list(db.all('test'))), 1)

        created = db.all('test').fetchone()
        self.assertEqual(created['name'], 't1')
        self.assertEqual(created['number'], 1)

    def test_db_updating(self):
        pass

    def test_db_deletion(self):
        pass

    def test_int_search(self):
        pass