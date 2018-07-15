import unittest
import os
import os.path

from OxygenRM.migrations import *

class CreatePosts(Migration):
    def create(self):
        posts = Table('posts')

        posts.create_cols(
            id=Col.Id(),
            title=Col.String(),
            body=Col.Text(null=True),
            user=Col.Rel('users'),

            timestamps=True
        )

        posts.create()

    def destroy(self):
        Table('posts').destroy()


class EditPosts(Migration):
    def mount(self):
        self.posts = Table.get('posts')

    def create(self):
        posts = self.posts

        posts.rename('publications')
        posts.drop_cols('edited_at')
        posts.rename_cols(title='Título')

        posts.edit()

    def destroy(self):
        posts = self.posts

        posts.rename('posts')
        posts.create_cols(edited_at=True)
        posts.rename_cols(Título='title')

        posts.edit()

class TestMigrations(unittest.TestCase):
    def test_migration_class_inits(self):
        pass

    def test_migration_created_ok(self):
        pass

    def test_migration_created_tables_and_cols(self):
        pass

    def test_migration_destroy_ok(self):
        pass

    def test_migration_destroy_works(self):
        pass

    def test_migration_follow_ups(self):
        pass

    def test_migration_cli_tool_inits(self):
        pass

    def test_migration_cli_creates_migration(self):
        pass

    def test_migration_cli_runs_migration(self):
        pass

    def test_migration_cli_undoes_migrations(self):
        pass

current_path = os.getcwd()
class TestMigrationHelpers(unittest.TestCase):
    def tearDown(self):
        os.rmdir(os.path.join(os.getcwd(), 'migrationsCLI'))

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