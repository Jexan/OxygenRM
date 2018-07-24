import unittest

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