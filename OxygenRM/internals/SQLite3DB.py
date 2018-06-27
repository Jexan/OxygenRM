''' The database driver for using a SQLite3 connection.
    Abstracts away the basic DB operations, to make everything
    easier for dealing internally with models.
'''
import sqlite3

class SQLite3DB():
    """ Init the connection to the database
    """
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor     = self.connection.cursor()

    def create_table(self, table_name, **cols):
        cols_parentheses = ','.join(col_name + ' ' + col_type for col_name, col_type in cols.items())
        query = 'CREATE TABLE {} ({})'.format(table_name, cols_parentheses) 

        self.execute(query)

        return True

    def table_info(self, table_name):
        keys = ['cid', 'column', 'type', 'notnull', 'dflt_value', 'pk']
        query = "PRAGMA table_info({})".format(table_name)

        self.execute(query)

        return [dict(zip(keys, row)) for row in self.cursor.fetchall()]

    def table_fields_types(self, table_name):
        info = self.table_info(table_name)

        return {col['column']: col['type'] for col in info}

    def drop_all_tables(self):
        pass

    def execute(self, query, args=()):
        self.cursor.execute(query, args)
        self.connection.commit()