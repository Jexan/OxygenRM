# The basic configuration needed to run your migrations
# and to display and log information when ran.

# -------------- Database configuration --------------

import OxygenRM as O

DB_DRIVER = 'sqlite3'
DB_NAME = ':memory:'

db = O.db_config(DB_DRIVER, DB_NAME)