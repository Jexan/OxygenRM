import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--init", "-i", 
    help="Start up the migrations dir and status file", 
)

parser.add_argument(
    "--create", "-c", 
    help="Create a migration", 
)

parser.add_argument(
    "--migrate", "-m", 
    help="Commit the given number of migrations. Negative numbers will rollback migrations",
)

parser.add_argument(
    "--reboot", "-r",
    help="Reset all migrations and recommit them all",
)

parser.add_argument(
    "--status", "-s", 
    help="Show the current migration version",
)

parser.add_argument(
    "--clean", "-r", 
    help="Clean up the migration numbers and order",
)

def init_migrations(folder="migrations"):
    # create the migration directory
    
    # create a config file. It should include "db_config data" and log status
    ...

def create_migration(name):
    # set up the name, using date and all
    # create a migration file and the class
    ...

def migrate(number):
    # determine if it should migrate or rollback

    # do error handling, if, for example, it's not possible to migrate the given number of migrations

    # warm that the migrations may be unordered
    ...

def reboot():
    # call migration with - #current migrations and recall it with +#total migrations
    ...

def status():
    # show the current status of the migrations
    ...

def clean():
    # reorders the files by number
    ...

def config(**options):
    # change the naming convention (by default it should be 01 - Create table Users)
    # to 01_create_table_users or 2018_10_17_045621_create_table_users
    ...

# Abstract base class for migrations 
class Migration():
    def call(self):
        pass

def set_from_last_migration():
    pass

class Database():
    def __init__(self, name):
        pass