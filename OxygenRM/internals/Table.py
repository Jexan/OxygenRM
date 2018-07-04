from enum import Enum
from functools import wraps

from OxygenRM import internal_db as db

class TableDoesNotExistError(Exception):
    ''' A exception to be raised when a method that involves
        editing an existing database is called. 
    '''
    pass

class ColumnAlreadyExistsError(Exception):
    ''' A exception to be raised when a column that already
        exist is tried to be created. 
    '''
    pass    

# Allows the creation, edition and droppage of tables
class Table():
    ''' Abstracts common database table operations.
        To be used mostly during migrations.

        Args:
            table_name: The table to deal with. It doesn't matter if it doesn't exist. 
    '''

    class State(Enum):
        ''' The possible states of the table.
        '''
        CREATING = 1
        EDITING  = 2

    # If the table already exists, grabs it. If not, it creates one.
    def __init__(self, table_name):
        self.table_name = table_name

        if db.table_exists(table_name):
            self.state = self.State.EDITING 
        else:
            self.state = self.State.CREATING

        self._assign_tables()
        self.table_columns = []

    def exists(self):
        ''' Check if the table exist in the database.

            Returns:
                bool.
        '''
        return self.state is self.State.EDITING

    def rename(self, new_name):
        ''' Change the name of the table.

            Args:
                name: The new name of the table

            Raises:
                TableDoesNotExistError: If the table is just being created.
        '''
        self._exists_guard()

        db.rename_table(self.table_name, new_name)

    def create_columns(self, timestamps=False, **columns):
        ''' Queue the creation of the given columns.

            Args:
                **columns: The column name = Column dict of columns to be created.
                
            Raises:
                TypeError: If the given columns are not subclasses of Column.
        '''
        for col_name, column_type in columns.items():
            if col_name in self.columns:
                raise ColumnAlreadyExistsError('The table {} aready has a column {}'.format(self.table_name, col_name))
            self._add_columns.append(column_type.get_data(col_name, db.driver))

    def drop_columns(self, *args):
        pass

    def rename_columns(self, **kwargs):
        pass

    def edit_columns_props(self, **kwargs):
        pass  

    def drop(self):
        ''' Destroy the table and deletes self.

            Raises:
                TableDoesNotExistError: If the table is just being created.
        '''
        self._exists_guard()

        db.drop_table(self.table_name)

    def drop_if_exists(self):
        ''' Destroy the table if exists.
        '''
        db.drop_table(self.table_name)

    def save(self):
        if self.exists():
            pass
        else:
            self._create()

    def _edit(self):
        pass

    def _create(self):
        if not self._add_columns:
            raise ValueError('No column has been specified to be added to the table')

        db.create_table(self.table_name, self._add_columns)

    def _assign_tables(self):
        ''' Fetch the table currently created columns.
        '''
        if self.exists():
            self.columns = {col.name: col for col in db.get_all_columns(self.table_name)}
        else:
            self.columns = {}

        self._edit_columns = []
        self._add_columns = []
        self._delete_columns = []

    def _exists_guard(self):
        ''' Halt execution if the table doesn't exist.

            Raises:
                TableDoesNotExistError: If the table is just being created.
        '''
        if not self.exists():
            raise TableDoesNotExistError('You can not edit a table that does not exist')