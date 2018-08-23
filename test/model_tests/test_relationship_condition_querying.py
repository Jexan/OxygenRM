from . import *
from .test_basic_model_relations import User, Post, OnePostUser, user_cols, post_cols
from .test_model_many_to_many import T1, T2, ts_cols, middle_cols

class TestSimpleRelations(unittest.TestCase):
    def setUp(self):
        db.drop_all_tables()

        db.create_table('users', user_cols)
        db.create_table('posts', post_cols)

        db.create_table('t1s', ts_cols)
        db.create_table('t2s', ts_cols)
        db.create_table('t1_t2', middle_cols)

    def test_has_relation_has(self):
        db.create('posts', text='t', author_id=2)
        db.create('users', username='t1')
        db.create('users', username='t2')

        rel = User.has('posts').first()
        self.assertEqual(rel.username, 't2')

        rel = OnePostUser.has('post').first()
        self.assertEqual(rel.username, 't2')    

    def test_has_relation_has_complex_queries(self):
        db.create('posts', text='t', author_id=2)
        db.create('users', username='t1')
        db.create('users', username='t2')

        rel = User.has('posts').where_not_null('username').where_in('username', set('t2')).delete()
        self.assertEqual(User.find(2), None)
        self.assertEqual(User.count(), 1)

    def test_has_relation_has_with_no_records_queries_none(self):
        db.create('posts', text='t', author_id=2)
        db.create('users', username='t1')

        rel = User.has('posts').first()
        self.assertIs(rel, None)

        rel = OnePostUser.has('post').first()
        self.assertIs(rel, None)

    def test_has_relation_multiple(self):
        T1.craft(False, id=1)
        db.create_many('t2s', ('id', ), [[1],[2],[3]])
        db.create('t1_t2', t1_id=1, t2_id=2)

        rel_container = T1.has('t2s').get()
        self.assertEqual(len(rel_container), 1)
        self.assertEqual(rel_container[0].id, 1)

        rel_container = T2.has('t1s').get()
        self.assertEqual(len(rel_container), 1)
        self.assertEqual(rel_container[0].id, 2)

    def test_where_pivot(self):
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
        T1.craft(False, id=1)
        db.create_many('t2s', ('id', ), [[1],[2],[3]])
        db.create('t1_t2', t1_id=1, t2_id=2)

        rel_container = T1.doesnt_have('t2s').get()
        self.assertEqual(len(rel_container), 0)

        rel_container = T2.doesnt_have('t1s').get()
        self.assertEqual(len(rel_container), 2)
        self.assertEqual(set(rel_container).pluck('id'), set(1, 3))

    def test_doesnt_have_relation_multiple_complex_query(self):
        T1.craft(False, id=1)
        db.create_many('t2s', ('id', ), [[1],[2],[3]])
        db.create('t1_t2', t1_id=1, t2_id=2)

        rel_container = T2.doesnt_have('t1s').where('id', '=', 1).limit(1).get()
        self.assertEqual(len(rel_container), 1)
        self.assertEqual(rel_container[0], 1)

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