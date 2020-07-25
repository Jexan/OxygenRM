import unittest
from itertools import chain
from OxygenRM.migrations import *

class TestMigrations(unittest.TestCase):
    def test_migration_class_inits(self):
        ...

    def test_migration_created_ok(self):
        ...

    def test_migration_created_tables_and_cols(self):
        ...

    def test_migration_destroy_ok(self):
        ...

    def test_migration_destroy_works(self):
        ...

    def test_migration_follow_ups(self):
        ...

    def test_migration_cli_tool_inits(self):
        ...

    def test_migration_cli_creates_migration(self):
        ...

    def test_migration_cli_runs_migration(self):
        ...

    def test_migration_cli_undoes_migrations(self):
        ...

current_path = os.getcwd()

@unittest.skip("Must find a better way to test all of this")
class TestMigrationHelpers(unittest.TestCase):
    def tearDown(self):
        created_files = []
        created_dirs = []

    def test_migration_dir_if_dir_not_exists(self):
        new_dir = 'migrationsCLI'
        new_dir_path = os.path.join(current_path, new_dir)
        migration_dir_path = migration_dir(new_dir)

        self.assertTrue(os.path.exists(new_dir_path))
        self.assertEqual(migration_dir_path, new_dir_path)
        
    def test_migration_dir_if_dir_not_exists(self):
        new_dir = 'migrationsCLI'
        new_dir_path = os.path.join(current_path, new_dir)
        
        os.mkdir(new_dir_path)

        migration_dir_path = migration_dir(new_dir)

        self.assertTrue(os.path.exists(new_dir_path))
        self.assertEqual(migration_dir_path, new_dir_path)    

    def test_migration_dir_ow_dir_not_exists(self):
        new_dir = 'migrationsCLI'
        new_dir_path = os.path.join(current_path, new_dir)
        
        os.mkdir(new_dir_path)

        migration_dir_path = migration_dir(new_dir)

        self.assertTrue(os.path.exists(new_dir_path))
        self.assertEqual(migration_dir_path, new_dir_path)    

    def test_migration_dir_creates_config_file(self):
        init_migrations()

        self.assertTrue(os.path.isfile(os.path.join(current_path, DEFAULT_MIGRATION_DIR, CONFIG_FILE_NAME)))
        
    def test_migration_dir_raises_ValueError_to_not_overwrite_an_existing_config_file(self):
        ...