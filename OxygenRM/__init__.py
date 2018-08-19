from OxygenRM.internals.SQLite3DB import *

internal_db = None
db = None

# Defines the database driver
def db_config(driver, db_name):
    global internal_db, db 
    
    if driver == 'sqlite3':
        internal_db = SQLite3DB(db_name)
        db = internal_db
        return internal_db
    
# Sets the database to a set database driver
def db_set():
    pass