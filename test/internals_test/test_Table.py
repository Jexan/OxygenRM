import unittest
from OxygenRM import db_config, internal_db

# FOR NOW
db = db_config('sqlite3', ':memory:')

from OxygenRM.internals.Table import *


def craft_generic_table():
    generic_cols = {'a': 'integer', 'b': 'text'}
    db.create_table('t', **generic_cols)

class TestTable(unittest.TestCase):
    def tearDown(self):
        db.drop_all_tables()

    def test_Table_initialization(self):
        table = Table('t')

        self.assertIsInstance(table, Table)

    def test_Table_state_is_set_correctly_at_creation_if_not_exists(self):
        table = Table('t')

        self.assertIs(table.state, Table.State.CREATING)

    def test_Table_state_is_set_correctly_at_creation_if_exists(self):
        craft_generic_table()
        table = Table('t')

        self.assertIs(table.state, Table.State.EDITING)

    def test_Table_edition_if_it_exists(self):
        pass

    def test_Table_behaviour_if_create_table_that_already_exists(self):
        pass

    def test_Table_destroying(self):
        pass
    
    def test_Table_destroying_if_table_not_exists(self):
        pass

    def test_Table_renaming(self):
        pass

    def test_Table_adding_cols(self):
        pass

    def test_Table_adding_cols_if_already_exists(self):
        pass

    def test_Table_renaming_cols(self):
        pass

    def test_Table_renaming_cols_if_none_exists(self):
        pass

    def test_Table_editing_cols_properties(self):
        pass