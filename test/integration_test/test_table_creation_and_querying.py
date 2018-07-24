from OxygenRM import db_config
from OxygenRM.internals.Table import Table
from OxygenRM.models import Model

import OxygenRM.internals.columns as c
import OxygenRM.internals.fields as f

db_config('sqlite3', ':memory:')

class Test(Model):
    id = f.Id()
    name = f.Text()

t = Table('tests')
t.create_columns(id=c.Id(), name=c.Text())  
t.save()

def create_table_and_make_queries():
    for i in range(10):
        Test(name=str(i+1)).save()

import unittest
import OxygenRM

class TestTableCreationAndQuerying(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        Table('tests').drop()        
    
    def test_db_init(self):
        self.assertIsInstance(OxygenRM.db, OxygenRM.internals.SQLite3DB.SQLite3DB)

    def test_table_was_created(self):
        self.assertTrue(Table('tests').exists())

    def test_table_has_corresponding_cols(self):
        tables_type = OxygenRM.db.table_fields_types('tests')
        self.assertEqual(tables_type, {'id': 'integer', 'name': 'text'})

    def test_models_created_correctly(self):
        create_table_and_make_queries()
        tests = Test.all()

        self.assertEqual(10, len(tests))
        for i, row in enumerate(tests, 1):
            self.assertEqual(row.id, i)
            self.assertEqual(row.name, str(i))