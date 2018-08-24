from enum import Enum
from functools import wraps

import OxygenRM as O
from OxygenRM.internals.columns import Column

class TableDoesNotExistError(Exception):
    """ A exception to be raised when a method that involves
        editing an existing database is called. 
    """
    pass

class ColumnAlreadyExistsError(Exception):
    """ A exception to be raised when a column that already
        exist is tried to be created. 
    """
    pass    

class ColumnDoesNotExistError(Exception):
    """ A exception to be raised when a column that does 
        not exist is attempted to be edited. 
    """
    pass    

# Allows the creation, edition and droppage of tables
class Table():
    """ Abstracts common database table operations.
        To be used mostly during migrations.

        Args:
            table_name: The table to deal with. It doesn't matter if it doesn't exist. 
    """

    class State(Enum):
        """ The possible states of the table.
        """
        CREATING = 1
        EDITING  = 2

    # If the table already exists, grabs it. If not, it creates one.
    def __init__(self, table_name):
        self.table_name = table_name

        if O.db.table_exists(table_name):
            self.state = self.State.EDITING 
        else:
            self.state = self.State.CREATING

        self._assign_tables()

    def exists(self):
        """ Check if the table exist in the database.

            Returns:
                bool.
        """
        return self.state is self.State.EDITING

    def rename(self, new_name):
        """ Change the name of the table.

            Args:
                name: The new name of the table

            Raises:
                TableDoesNotExistError: If the table is just being created.
        """
        self._exists_guard()

        self._new_name = new_name

    def create_columns(self, timestamps=False, **columns):
        """ Queue the creation of the given columns.

            Args:
                **columns: The column name = Column dict of columns to be created.
            
            Returns:
                self
                
            Raises:
                TypeError: If the given columns are not subclasses of Column.
        """
        for col_name, column_type in columns.items():
            if col_name in self._current_columns:
                raise ColumnAlreadyExistsError('The table {} aready has a column {}'.format(self.table_name, col_name))

            column_type.name = col_name
            self._add_columns[col_name] = column_type.get_data(O.db.driver)

        return self

    def drop_columns(self, *columns):
        """ Queue the droppage of the given columns.

            Args:
                *columns: The columns name to be dropped.
            
            Returns:
                self

            Raises:
                TableDoesNotExistError: If the table does not exist.
                columnDoesNotExistsError: If the column to drop does not exist in the table.
        """
        self._exists_guard()

        for col in columns:
            if col not in self._current_columns:
                raise ColumnDoesNotExistError('Cannot drop column {} that does not exist.'.format(col))

            self._current_columns[col].drop()

        return self

    def drop(self):
        """ Destroy the table and deletes self.

            Raises:
                TableDoesNotExistError: If the table is just being created.
        """
        self._exists_guard()

        O.db.drop_table(self.table_name)

    def drop_if_exists(self):
        """ Destroy the table if exists.
        """
        O.db.drop_table(self.table_name)

    def save(self):
        if self.exists():
            self._edit()
        else:
            self._create()

        self._assign_tables()

        return self

    def _edit(self):
        driver = O.db.driver

        old_cols = self._columns_data
        cols_to_add  = self._add_columns.values()

        cols_to_drop = {col_name: col.get_data(driver) for col_name, col in self._current_columns.items() if col.to_be_dropped}
        cols_to_edit = {col_name: col.get_data(driver) for col_name, col in self._current_columns.items() if col.to_be_editted}

        if cols_to_add or cols_to_drop or cols_to_edit:
            O.db.modify_columns(self.table_name, cols_to_add, cols_to_drop, cols_to_edit, old_cols)

        if self._new_name:
            O.db.rename_table(self.table_name, self._new_name)
            
            self.table_name = self._new_name
            self._new_name = None
 
    def _create(self):
        if not self._add_columns:
            raise ValueError('No column has been specified to be added to the table')

        O.db.create_table(self.table_name, self._add_columns.values())

        self.state = self.State.EDITING

    def _assign_tables(self):
        """ Fetch the table currently created columns.
        """
        if self.exists():
            col_data = tuple(O.db.get_all_columns(self.table_name))

            self._columns_data = {col.name: col for col in col_data}
            self._current_columns = {col.name: Column.from_data(col, O.db.driver) for col in col_data}
        else:
            self._current_columns = {}

        self._edit_columns = {}
        self._add_columns = {}
        self._delete_columns = []

    def _exists_guard(self):
        """ Halt execution if the table doesn't exist.

            Raises:
                TableDoesNotExistError: If the table is just being created.
        """
        if not self.exists():
            raise TableDoesNotExistError('You can not edit a table that does not exist')

    def __setattr__(self, attr, value):
        if isinstance(value, Column):
            if attr not in self._add_columns:
                self.create_columns(**{attr: value}) 
            else:
                self.edit_columns(**{attr: value})
        else:
            super().__setattr__(attr, value)

    def __getattr__(self, attr):
        return self._current_columns.get(attr, None)