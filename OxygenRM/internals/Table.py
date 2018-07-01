from .. import internal_db as db
from enum import Enum

class TableDoesNotExistException(Exception):
    ''' A exception to be raised when a method that involves
        editing an existing database is called. 
    '''
    pass    

# Allows the creation, edition and droppage of tables
class Table():
    ''' Abstracts common database table operations.
        To be used mostly during migrations.

        Args:
            table_name: The table to deal with. It doesn't matter if it doesn't exist. 
    '''

    ''' The possible states of the table
    '''
    class State(Enum):
        CREATING = 1
        EDITING  = 2

    # If the table already exists, grabs it. If not, it creates one.
    def __init__(self, table_name):
        if db.table_exists(table_name):
            self.state = self.State.EDITING 
        else:
            self.state = self.State.CREATING

        self.table_name = table_name

    def exists(self):
        ''' Check if the table exist in the database.

            Returns:
                bool.
        '''
        return self.state is self.State.EDITING

    # Allows adding columns to a table
    def create_cols(self, **kwargs):
        pass

    def rename(self, name):
        pass

    def drop_cols(self, *args):
        pass

    def rename_cols(self, **kwargs):
        pass

    def edit_cols_props(self, **kwargs):
        pass  

    def destroy(self):
        ''' Destroy the table and deletes self.

            Raises:
                TableDoesNotExistException: If the table is just being created.
        '''
        if not self.exists():
            raise TableDoesNotExistException('A non existing table cannot be destroyed')

        db.drop_table(self.table_name)

    def save(self):
        pass

    def __edit(self):
        pass

    def __create(self):
        pass