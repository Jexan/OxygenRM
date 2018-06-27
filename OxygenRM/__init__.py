from OxygenRM.internals.SQLite3DB import *
internal_db = None

# Defines the database driver
def db_config(driver, db):
    if driver == 'sqlite3':
        internal_db = SQlite3DB(db)
    
# Sets the database to a set database driver
def db_set():
    pass