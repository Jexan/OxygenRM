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
    
    def test_table_info(self):
        create_table('test', name= 'name', type='text')
        info = db.table_info('test')

        self.assertEqual(len(info), 1)

        # Check if the info dict is correct.
        self.assertEqual(info[0]['column_name'], 'name')
        self.assertEqual(info[0]['type'], 'text')
        self.assertEqual(info[0]['cid'], 0)

    def test_table_creation(self):
        db.create_table('test', name='text', age='integer')
        info = db.table_info('test')

        # Since dicts are not ordered.
        if info[0]['column'] == 'name':
            name_col = info[0]
            age_col  = info[1]
        else: 
            name_col = info[1]
            age_col  = info[0]
 
        self.assertEqual(len(info), 2)

        self.assertEqual(name_col['column_name'], 'name')
        self.assertEqual(age_col['column_name'], 'age')

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

    def test_db_updating(self):
        pass

    def test_db_deletion(self):
        pass

    def test_int_search(self):
        pass