from OxygenRM.internals.SQLite3DB import *

internal_db = None
db = None
handle_events = False
emit_warnings = True

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

def transaction():
    if not db:
        raise RuntimeError('Cannot start a transaction with an unspecified database.')
    else: 
        return db.transaction()

def use_events():
    global handle_events
    
    handle_events = True

def cancel_events():
    global handle_events

    handle_events = False

def warn(msg):
    """ Print a warning, if they're enabled.
    """
    if not emit_warnings:
        return
    else:
        print(f'OxigenRM warning: {msg}')