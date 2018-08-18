from . import *
from .test_basic_model_relations import User, Post, OnePostUser, user_cols, post_cols

class TestSimpleRelations(unittest.TestCase):
    def setUp(self):
        db.drop_table('posts')
        db.drop_table('users')
        db.create_table('users', user_cols)
        db.create_table('posts', post_cols)

    def test_has_relation_has(self):
        db.create('posts', text='t', author_id=2)
        db.create('users', username='t1')
        db.create('users', username='t2')

        rel = User.has('posts').first()
        self.assertEqual(rel.username, 't2')

        rel = OnePostUser.has('post').first()
        self.assertEqual(rel.username, 't2')

    def test_has_relation_has_with_no_records_queries_none(self):
        db.create('posts', text='t', author_id=2)
        db.create('users', username='t1')

        rel = User.has('posts').first()
        self.assertIs(rel, None)

        rel = OnePostUser.has('post').first()
        self.assertIs(rel, None)

    def test_has_relation_multiple(self):
        ...

    def test_has_relation_belongsTo_one(self):
        db.create('posts', text='t', author_id=1)
        db.create('users', username='t1')

        rel = Post.has('author').first()
        self.assertEqual(rel.text, 't')

    def test_has_relation_belongTOne_with_no_records_queries_none(self):
        db.create('posts', text='t', author_id=2)
        db.create('users', username='t1')

        rel = Post.has('author').first()
        self.assertIs(rel, None)

    def test_doesnt_have_relation_has(self):
        db.create('posts', text='t', author_id=2)
        db.create('users', username='t1')
        db.create('users', username='t2')

        rel = User.doesnt_have('posts').first()
        self.assertEqual(rel.username, 't1')

        rel = OnePostUser.doesnt_have('post').first()
        self.assertEqual(rel.username, 't1')

    def test_has_relation_doesnt_have_with_records_queries_none(self):
        db.create('posts', text='t', author_id=1)
        db.create('users', username='t1')

        rel = User.doesnt_have('posts').first()
        self.assertIs(rel, None)

        rel = OnePostUser.doesnt_have('post').first()
        self.assertIs(rel, None)

    def test_doesnt_have_relation_multiple(self):
        ...

    def test_doesnt_have_relation_belongsTo_one(self):
        db.create('posts', text='t', author_id=3)
        db.create('users', username='t1')

        rel = Post.doesnt_have('author').first()
        self.assertEqual(rel.text, 't')

    def test_doesnt_have_relation_belongsTo_one_even_if_null(self):
        db.create('posts', text='t', author_id=None)
        db.create('users', username='t1')

        rel = Post.doesnt_have('author').first()
        self.assertEqual(rel.text, 't')

    def test_doesnt_have_relation_belongsTo_one_with_all_rels_yields_none(self):
        db.create('posts', text='t', author_id=1)
        db.create('users', username='t1')

        self.assertIs(Post.doesnt_have('author').first(), None)

        db.create('posts', text='t', author_id=None)
        self.assertEqual(Post.doesnt_have('author').first().text, 't')