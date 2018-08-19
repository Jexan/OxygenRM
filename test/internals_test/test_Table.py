import unittest

from OxygenRM import db
from OxygenRM.internals.Table import *
from OxygenRM.internals.columns import *

from . import default_cols

created_table = Table('c')

db.create_table('e', default_cols(a='integer', b='text'))
edited_table = Table('e')

class TestTable(unittest.TestCase):
    def tearDown(self):
        db.drop_table('t')

    def test_Table_initialization(self):
        self.assertIsInstance(edited_table, Table)
        self.assertIsInstance(created_table, Table)

    def test_Table_state_is_set_correctly_at_creation_if_not_exists(self):
        self.assertIs(created_table.state, Table.State.CREATING)
        self.assertFalse(created_table.exists())

    def test_Table_state_is_set_correctly_at_creation_if_exists(self):
        self.assertIs(edited_table.state, Table.State.EDITING)
        self.assertTrue(edited_table.exists())

    def test_drop_raises_exception_if_table_doesnt_exist(self):
        self.assertRaises(TableDoesNotExistError, created_table.drop)

    def test_Table_droping(self):
        db.create_table('t', default_cols(a='text'))
        table = Table('t')

        table.drop()

        self.assertFalse(db.table_exists('t'))
    
    def test_Table_droping_if_table_not_exists(self):
        self.assertRaises(TableDoesNotExistError, created_table.drop)

    def test_Table_drop_if_exist_drops_correctly(self):
        db.create_table('t', default_cols(a='text'))
        table = Table('t')

        table.drop_if_exists()

        self.assertFalse(db.table_exists('t'))

    def test_Table_drop_if_exists_continues_if_table_not_exists(self):
        Table('t').drop_if_exists()

    def test_Table_renaming(self):
        db.create_table('t', default_cols(a='text'))
        
        table = Table('t')
        table.rename('s')
        table.save()

        self.assertFalse(db.table_exists('t'))
        self.assertTrue(db.table_exists('s'))
    
    def test_new_Table_adding_cols(self):
        t = Table('t')
        t.create_columns(name=Text(), number=Integer())
        t.save()

        self.assertTrue(db.table_exists('t'))
        self.assertEqual(db.table_fields_types('t'), {'name': 'text', 'number': 'integer'})

    def test_Table_adding_cols_with_object_syntax(self):
        t = Table('t')
        t.text = Text()
        t.number = Integer()
        t.save()

        self.assertTrue(db.table_exists('t'))
        self.assertEqual(db.table_fields_types('t'), {'text': 'text', 'number': 'integer'})

class TestTableColumnsEdition(unittest.TestCase):
    def setUp(self):
        db.drop_table('t')

        t = Table('t')
        t.text = Text()
        t.save()

    def test_columns_of_created_table_are_accesible(self):
        t = Table('t')

        self.assertIsInstance(t.text, Text)

    def test_existing_Table_adding_cols(self):
        t = Table('t')
        t.number = Integer()
        t.save()
        
        self.assertEqual(db.table_fields_types('t'), {'text': 'text', 'number': 'integer'})

    def test_Table_adding_cols_if_already_exists_raises_ColumnAlreadyExistsError(self):
        with self.assertRaises(ColumnAlreadyExistsError): 
            Table('t').create_columns(text=Text())
    
    def test_Table_making_cols_null(self):
        t = Table('t')
        t.text.null = False
        t.save()

        self.assertFalse(Table('t').text.null)    

    def test_Table_making_cols_with_default(self):
        t = Table('t')
        t.text.null = False
        t.save()

        self.assertFalse(Table('t').text.null)    
    
    def test_renaming_existing_col(self):
        t = Table('t')
        t.text.name = 'text2'
        t.save()

        self.assertEqual(db.table_fields_types('t'), {'text2': 'text'})
    
    def test_dropping_all_cols_raise_valueError(self):
        t = Table('t')
        t.text.drop()
        self.assertRaises(ValueError, t.save)