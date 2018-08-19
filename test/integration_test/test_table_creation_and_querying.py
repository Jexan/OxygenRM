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

def create_10_records():
    for i in range(10):
        Test(name=str(i+1)).save()

def get_the_records_5_6():
    return Test.where_in('id', (5,6)).get()

import unittest
import OxygenRM

class TestTableCreationAndQuerying(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        Table('tests').drop()        

    def tearDown(self):
        Test.truncate()
    
    def test_db_init(self):
        self.assertIsInstance(OxygenRM.db, OxygenRM.internals.SQLite3DB.SQLite3DB)

    def test_table_was_created(self):
        self.assertTrue(Table('tests').exists())

    def test_table_has_corresponding_cols(self):
        tables_type = OxygenRM.db.table_fields_types('tests')
        self.assertEqual(tables_type, {'id': 'integer', 'name': 'text'})

    def test_models_created_correctly(self):
        create_10_records()
        tests = Test.all()

        self.assertEqual(10, len(tests))
        for i, row in enumerate(tests, 1):
            self.assertEqual(row.name, str(i))

    def test_model_in_integration(self):
        create_10_records()
        records = get_the_records_5_6()

        self.assertEqual(records.first().id, 5)
        self.assertEqual(records[1].id, 6)