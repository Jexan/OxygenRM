import argparse
import os
import os.path

if __name__ == '__main__':
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
        action='store_true'
    )

    parser.add_argument(
        "--status", "-s", 
        help="Show the current migration version",
        action='store_true'
    )

    parser.add_argument(
        "--clean", "-cu", 
        help="Clean up the migration numbers and order",
        action='store_true'
    )

DEFAULT_MIGRATION_DIR = 'migrations'

# -----------------------------------
def migration_dir(directory):
    ''' Prepare the given directory for doing migrations

        Args:
            directory: The directory to use for the migrations 

        Returns:
            The path of the migration directory
    '''
    path = os.path.join(os.getcwd(), directory)

    if not os.path.isdir(path):
        os.mkdir(path)

    return path

# ------------------------------------
def init_migrations(rel_directory=None):
    ''' Start up the migration config and directory

        Args:
            rel_directory: The directory to use for the migrations 
    '''
    if rel_directory is None:
        rel_directory = DEFAULT_MIGRATION_DIR

    directory_path = migration_dir(rel_directory)
    
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