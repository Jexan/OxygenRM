import unittest

from OxygenRM import db
from OxygenRM.internals.Table import *
from OxygenRM.internals.columns import *
from OxygenRM.testing import print_queries

from . import default_cols


class TestTable(unittest.TestCase):
    def tearDown(self):
        Table.drop_all()

    @classmethod
    def setUpClass(cls):
        db.create_table('e', default_cols(a='integer', b='text'))

        cls.created_table = Table('c')
        cls.edited_table = Table('e')

    def test_Table_initialization(self):
        self.assertIsInstance(self.edited_table, Table)
        self.assertIsInstance(self.created_table, Table)

    def test_Table_state_is_set_correctly_at_creation_if_not_exists(self):
        self.assertIs(self.created_table.state, Table.State.CREATING)
        self.assertFalse(self.created_table.exists())

    def test_Table_state_is_set_correctly_at_creation_if_exists(self):
        self.assertIs(self.edited_table.state, Table.State.EDITING)
        self.assertTrue(self.edited_table.exists())

    def test_drop_raises_exception_if_table_doesnt_exist(self):
        self.assertRaises(TableDoesNotExistError, self.created_table.drop)

    def test_Table_droping(self):
        db.create_table('t', default_cols(a='text'))
        table = Table('t')

        table.drop()

        self.assertFalse(db.table_exists('t'))
    
    def test_Table_droping_if_table_not_exists(self):
        self.assertRaises(TableDoesNotExistError, self.created_table.drop)

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
    
    def test_new_Table_adding_cols_with_expression(self):
        with Table('t') as t:
            t.create_columns(name=Text(), number=Integer())

        self.assertTrue(db.table_exists('t'))
        self.assertEqual(db.table_fields_types('t'), {'name': 'text', 'number': 'integer'})

    def test_Table_adding_cols_with_object_syntax(self):
        t = Table('t')
        t.text = Text()
        t.number = Integer()
        t.save()

        self.assertTrue(db.table_exists('t'))
        self.assertEqual(db.table_fields_types('t'), {'text': 'text', 'number': 'integer'})

    def test_Table_adding_foreing_constaints(self):
        with Table('s') as s:
            s.t = Integer()

        t = Table('t')
        t.text = Text()
        t.text.references = 's (t)'
        t.save()

        db.create('t', text='ay')

        self.assertTrue(db.table_exists('t'))

class TestTableColumnsEdition(unittest.TestCase):
    def setUp(self):
        db.drop_table('t')

        with Table('t') as t:
            t.text = Text()

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