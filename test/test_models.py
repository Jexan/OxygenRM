# Test cases for OxygenRM Models

import unittest

from OxygenRM import db
from OxygenRM.internals.ModelContainer import ModelContainer
from .internals_test import default_cols

import OxygenRM.models as O

from OxygenRM.internals.fields import *

##############################################################

class Todo(O.Model):
    a = Text()

class TestModels(unittest.TestCase):
    def tearDown(self):
        db.drop_all_tables()

    def setUp(self):
        db.create_table('todos', default_cols(a='text'))

    def test_model_initialization(self):
        t = Todo()

        self.assertIsInstance(t, Todo)
        self.assertIsInstance(t, O.Model)

    def test_model_field_set_up_correctly(self):
        db.create_table('tests', default_cols(a='text'))
        class Test(O.Model):
            a = Text()

        t = Test()
        t.a = 'hey'
        self.assertEqual(t.a, 'hey')

        with self.assertRaises(TypeError):
            t.a = 12

    def test_model_is_set_up_if_invoked(self):
        t = Todo()
        self.assertTrue(Todo._set_up)

        self.assertEqual(Todo.table_name, 'todos')

    def test_model_is_set_up_if_chained(self):
        db.create_table('users', default_cols(a='text'))
        class User(O.Model):
            a = Text()

        User.limit(2).get()

        self.assertTrue(User._set_up)
        self.assertEqual(User.table_name, 'users')

    def test_model_is_not_set_up_if_not_invoked(self):
        db.create_table('users', default_cols(a='text'))
        class User(O.Model):
            a = Text

        self.assertFalse(User._set_up)
        self.assertEqual(User.table_name, '')

    def test_model_can_have_custom_table_name(self):
        db.create_table('murder', default_cols(name='text'))
        class Crow(O.Model):
            table_name = 'murder'

            name = Text()

        Crow()

        self.assertEqual(Crow.table_name, 'murder')

    def test_model_where_queries(self):
        create_todo()

        t = Todo.where('a', '=', 't').get().first()

        record = db.all('todos').fetchone()
        self.assertEqual(t.a, record['a'])

    def test_multiple_models_dont_get_screwed_up(self):
        create_todo()
        create_todo()

        t = Todo.all().first()
        t.a = 's'

        e = Todo.all()[1]
        e.a = 't'

        self.assertNotEqual(t.a, e.a)

    def test_weird(self):
        class R:
            pass

        R.e = Integer()
        a = R()
        b = R()

        a.e = 1
        b.e = 3

        self.assertNotEqual(a, b)

    def test_model_limit(self):
        for i in range(100):
            create_todo()

        exists = db.table_exists('todos')
        first_50_todos = list(Todo.limit(50).get())

        self.assertEqual(len(first_50_todos), 50)

    def test_models_new(self):
        t = Todo()
        t.a = 't'

        self.assertEqual(t.a, 't')

        t.save()

        record = db.all('todos').fetchone()
        self.assertEqual(record['a'], 't')

        s = Todo()
        t.a = 't2'

        self.assertEqual(t.a, 't2')
        t.save()

        record = list(db.all('todos'))[-1]
        self.assertEqual(record['a'], 't2')

    def test_models_destroy(self):
        create_todo()

        t = Todo.where('a', '=', 't').first()
        t.destroy()

        record = db.all('todos').fetchone()
        self.assertIs(record, None)

    def test_models_delete(self):
        create_todo()

        t = Todo.where('a', '=', 't').delete()

        record = db.all('todos').fetchone()
        self.assertIs(record, None)

    def test_model_update(self):
        create_todo()

        t = Todo.where('a', '=', 't').first()

        t.a = 's'
        t.save()

        all_records = list(db.all('todos'))
        self.assertEqual(len(all_records), 1)

        record = all_records[0]

        self.assertEqual(record['a'], 's')

def create_todo():
    db.create('todos', a='t')

##############################################################

class User(O.Model):
    id = Id()
    username = Text()

class Post(O.Model):
    id = Id()
    text = Text()
    author_id = Integer()

    author = BelongsTo('one', User, on_self_col='author_id')

User.posts = Has('many', Post, on_other_col="author_id")

class OnePostUser(O.Model):
            table_name = 'users'

            id = Id()
            username = Text()
            post = Has('one', Post, on_other_col='author_id')

user_cols = [
    next(default_cols(id='integer'))._replace(primary=True, auto_increment=True),
    next(default_cols(username='text'))
]

post_cols = [
    next(default_cols(id='integer'))._replace(primary=True, auto_increment=True),
] + list(default_cols(text='text', author_id='integer'))

User()
Post()
OnePostUser()

# @unittest.skip('Not yet finished')
class TestSimpleRelations(unittest.TestCase):
    def setUp(self):
        db.drop_table('posts')
        db.drop_table('users')
        db.create_table('users', user_cols)
        db.create_table('posts', post_cols)

    def test_models_with_rels_initializing_correctly(self):
        self.assertIsInstance(User(), User)
        self.assertIsInstance(Post(), Post)

        self.assertIsInstance(User._relations['posts'], Has)
        self.assertIsInstance(Post._relations['author'], BelongsTo)

    def test_has_queries_correctly_with_one_related_model(self):
        db.create_many('users', ('username', ), (('t1',),))
        db.create_many('posts', ('text', 'author_id'), (('t', 1),))

        user_post = User.first().posts
        self.assertIsInstance(user_post, QueryBuilder)

        bullshit_i_have_to_do_because_the_test_are_fucking_broken = user_post.first()
        pure_post = Post.first()
        self.assertEqual(bullshit_i_have_to_do_because_the_test_are_fucking_broken, pure_post)

    def test_that_models_has_key_access_is_not_broken_on_simple_methods(self):
        db.create_many('users', ('username', ), (('t1',),))
        db.create_many('posts', ('text', 'author_id'), (('t', 1),))

        def get_text(model):
            return model.text

        posts = User.first().posts.get()
        self.assertEqual('t', get_text(posts[0]))

    def test_has_with_no_result_queries_empty(self):
        db.create_many('users', ('username', ), (('t1',),))

        user_post = User.first().posts

        self.assertEqual(len(user_post.get()), 0)

    def test_has_queries_correctly_with_multiple_related_model(self):
        db.create_many('users', ('username', ), (('t1',),))
        db.create_many('posts', ('text', 'author_id'), (('t', 1), ('s', 1), ('r', 1)))

        user_posts = User.first().posts.get()

        self.assertEqual(len(user_posts), 3)
        self.assertEqual(user_posts[2].text, 'r')
        self.assertEqual(user_posts[1].text, 's')

    def test_has_queries_correctly_even_with_other_unrelated_models_present(self):
        db.create_many('users', ('username', ), (('t1',),))
        db.create_many('posts', ('text', 'author_id'), (('t', 1), ('s', 2)))

        user_posts = User.first().posts.get()

        self.assertEqual(len(user_posts), 1)
        self.assertEqual(user_posts.first().text, 't') 

    def test_has_assigning_one(self):
        db.create_many('users', ('username', ), (('t1',),))
        db.create_many('posts', ('text', 'author_id'), (('t', 2),))
        
        user = User.first()
        user.posts.assign(Post.first())

        user.save()

        self.assertEqual(User.first().posts.get()[0], Post.first())
        self.assertEqual(1, Post.first().author_id)
        
    def test_has_assigning_some(self):
        db.create_many('users', ('username', ), (('t1',), ('t2',)))
        db.create_many('posts', ('text', 'author_id'), (('t', 2), ('s', 2)))
        
        user = User.get()[0]
        user.posts.add_many(Post.get())
        user.save()

        user_posts = User.get()[0].posts.get()

        self.assertEqual(len(user_posts), 2)
        self.assertEqual(user_posts[0].text, 't')
        self.assertEqual(user_posts[1].text, 's')

    def test_has_reassigning_some(self):
        db.create_many('users', ('username', ), (('t1',), ('t2',)))
        db.create_many('posts', ('text', 'author_id'), (('t', 1), ('s', 2), ('r', 2)))
        
        posts_not_belong_to_1 = Post.where('id', '!=', 1).get()

        user = User.get()[0]
        user.posts.reassign(posts_not_belong_to_1)
        user.save()

        user_posts = User.get()[0].posts.get()

        self.assertEqual(len(user_posts), 2)
        self.assertEqual(user_posts[0].text, 's')
        self.assertEqual(user_posts[1].text, 'r')

    def test_deassigning_all(self):
        db.create_many('users', ('username', ), (('t1',),))
        db.create_many('posts', ('text', 'author_id'), (('t', 1), ('s', 2)))
        
        user = User.first()
        user.posts.deassign()
        user.save()

        user_posts = User.get()[0].posts.get()

        self.assertEqual(len(user_posts), 0)

    def test_has_adding_one(self):
        db.create_many('users', ('username', ), (('t1',),))
        db.create_many('posts', ('text', 'author_id'), (('t', 2), ('s', 1)))
        user = User.first()
        user.posts.add(Post.first())
        user.save()

        user_posts = User.first().posts.get()

        self.assertEqual(len(user_posts), 2)
        self.assertEqual(user_posts[0].text, 't')
        self.assertEqual(user_posts[1].text, 's')

    def test_has_one_works(self):
        db.create_many('users', ('username', ), (('t1',),))
        db.create_many('posts', ('text', 'author_id'), (('s', 1),))

        post = OnePostUser.first().post

        self.assertIsInstance(post, Post)
    
    def test_has_one_assignal(self):
        db.create_many('users', ('username', ), (('t1',),))
        db.create_many('posts', ('text', 'author_id'), (('t', 2), ('s', 1)))

        user = OnePostUser.first()
        post = user.post

        post.assign(Post.first())
        user.save()

        self.assertEqual(Post.first().author_id, 1)
        self.assertEqual(Post.get()[1].author_id, None)

    def test_has_one_deassignal(self):
        db.create_many('users', ('username', ), (('t1',),))
        db.create_many('posts', ('text', 'author_id'), (('s', 1),))

        user = OnePostUser.first()
        post = user.post

        post.deassign()
        
        user.save()
        self.assertEqual(Post.first().author_id, None)
        
    # Belongs To!
    def test_belongsTo_queries_correctly_with_one_related_model(self):
        db.create_many('users', ('username', ), (('t1',),))
        db.create_many('posts', ('text', 'author_id'), (('t', 1),))

        post_author = Post.first().author

        self.assertIsInstance(post_author, User)

        pure_user = User.first()
        self.assertEqual(post_author, pure_user)

    def test_belongsTo_queries_correctly_even_with_other_unrelated_models_present(self):
        db.create_many('users', ('username', ), (('t1',), ('t2',)) )
        db.create_many('posts', ('text', 'author_id'), (('t', 1),))

        post_author = Post.first().author
        pure_user = User.first()

        self.assertIsInstance(post_author, User)
        self.assertEqual(post_author.username, 't1')

    def test_belongTo_with_no_records_gets_a_none(self):
        db.create_many('posts', ('text', 'author_id'), (('t', 1),))
        
        post_author = Post.first().author

        self.assertIs(post_author, None)

##############################################################

class T1(O.Model):
    id = Id()

class T2(O.Model):
    id = Id()
    t1s = Multiple(T1)
    
T1.t2s = Multiple(T2)

ts_cols = next(default_cols(id='integer'))._replace(primary=True, auto_increment=True)

@unittest.skip('Not yet implemented')
class TestManyToMany(unittest.TestCase):
    def setUp(self):
        db.drop_table('t1')
        db.drop_table('t2')
        db.drop_table('t1s_t2s')
        
        db.create_table('t1', (ts_cols, ))
        db.create_table('t2', (ts_cols, ))
        db.create_table('t1s_t2s', default_cols(t1_id='integer', t2_id='integer'))

    def test_initialization_ok(self):
        self.assertIsInstance(T1(), T1)
        self.assertIsInstance(T2(), T2)

        self.assertIsInstance(T1.t2s, Multiple)
        self.assertIsInstance(T2.t1s, Multiple)

    def test_many_to_many_with_one_works(self):
        db.create_many('t1', (), ((),))
        db.create_many('t2', (), ((),))
        db.create_many('t1s_t2s', ('t1_id', 't2_id'), ((1,1),))

        first_t2 = T1.first().t2s.first()
        self.assertEqual(first_t2.id, 1)

        first_t1 = T2.first().t1s.first()
        self.assertEqual(first_t1.id, 1)

    def test_many_to_many_with_zero_its_an_empty_collection(self):
        db.create_many('t1', (), ((),))
        db.create_many('t2', (), ((),))

        first_t2 = T1.first().t2s
        self.assertEqual(len(first_t2), 0)

        first_t1 = T2.first().t1s
        self.assertEqual(len(first_t1), 0)

    def test_many_to_many_with_multiple_work(self):
        db.create_many('t1', (), ((),))
        db.create_many('t2', (), ((),)*4)
        db.create_many('t1s_t2s', ('t1_id', 't2_id'), tuple((1, i) for i in range(1, 5)))

        t2s = T1.first().t2s
        self.assertEqual(len(t2s), 4)
        self.assertTrue(all(t2.t1s.first().id == 1 for t2 in t2s))


##############################################################

class JsonModel(O.Model):
    a = JSON()

class TestJSONFields(unittest.TestCase):
    def setUp(self):
        db.create_table('JsonModels', default_cols(a='json'))

    def tearDown(self):
        db.drop_table('JsonModels')

    def test_initialization_of_class(self):
        self.assertIsInstance(JsonModel.a, JSON)

    def test_model_initialization(self):
        t1 = JsonModel()

        self.assertIsInstance(t1.a, JSON.JSONableDict)