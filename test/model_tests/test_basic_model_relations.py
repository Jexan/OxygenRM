from . import *

class User(O.Model):
    id = Id()
    username = Text()

    @classmethod
    def relations(cls):
        cls.posts = Has('many', Post, on_other_col="author_id")

class Post(O.Model):
    id = Id()
    text = Text()
    author_id = Integer()

    @classmethod
    def relations(cls):
        cls.author = BelongsTo('one', User, on_self_col='author_id')

class OnePostUser(O.Model):
    table_name = 'users'

    id = Id()
    username = Text()

    @classmethod
    def relations(cls):
        cls.post = Has('one', Post, on_other_col='author_id')

User.set_up()
Post.set_up()
OnePostUser.set_up()

class BaseClass(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.posts = Table('posts').create_columns(
            id=c.Id(),
            author_id=c.Integer(),
            text=c.Text()
        ).save()

        cls.users = Table('users').create_columns(
            id=c.Id(),
            username=c.Text()
        ).save()

    @classmethod
    def tearDownClass(cls):
        cls.posts.drop()
        cls.users.drop()

    def setUp(self):
        Post.truncate()
        User.truncate()
    
class TestSimpleRelations(BaseClass):
    def test_models_with_rels_initializing_correctly(self):
        self.assertIsInstance(User(), User)
        self.assertIsInstance(Post(), Post)

        self.assertIsInstance(User._relations['posts'], Has)
        self.assertIsInstance(Post._relations['author'], BelongsTo)

    def test_has_queries_correctly_with_one_related_model(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('t', 1),))

        user_post = User.first().posts
        self.assertIsInstance(user_post, ModelContainer)

        self.assertEqual(user_post.first(), Post.first())

    def test_has_queries_correctly_with_one_related_model_eagerly_loaded(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('t', 1),))

        user_post = User.with_relations('posts').first()
        self.assertIsInstance(user_post, User)
        self.assertIsInstance(user_post.relations_loaded['posts'], ModelContainer)

    def test_that_models_has_key_access_is_not_broken_on_simple_methods(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('t', 1),))

        posts = User.first().posts
        self.assertEqual('t', posts[0].text)

    def test_has_with_no_result_queries_empty(self):
        db.create('users', username='t1')

        user_post = User.first().posts
        self.assertEqual(len(user_post), 0)

    def test_has_queries_correctly_with_multiple_related_model(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('t', 1), ('s', 1), ('r', 1)))

        user_posts = User.first().posts

        self.assertEqual(len(user_posts), 3)
        self.assertEqual(user_posts[2].text, 'r')
        self.assertEqual(user_posts[1].text, 's')

    def test_has_queries_correctly_even_with_other_unrelated_models_present(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('t', 1), ('s', 2)))

        user_posts = User.first().posts

        self.assertEqual(len(user_posts), 1)
        self.assertEqual(user_posts.first().text, 't') 

    def test_has_one_works(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('s', 1),))

        post = OnePostUser.first().post

        self.assertIsInstance(post, Post)

    # Belongs To!
    def test_belongsTo_queries_correctly_with_one_related_model(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('t', 1),))

        post_author = Post.first().author

        self.assertIsInstance(post_author, User)

        pure_user = User.first()
        self.assertEqual(post_author.to_dict(), pure_user.to_dict())

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

        self.assertFalse(post_author)

class TestRelationEditing(BaseClass):
    def test_has_assigning_one(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('t', 2),))
        
        user = User.first()
        user.rel('posts').assign(Post.first()).save()

        self.assertEqual(1, Post.first().author_id)
        self.assertEqual(User.first().posts[0], Post.first())
        
    def test_has_assigning_some(self):
        db.create_many('users', ('username', ), (('t1',), ('t2',)))
        db.create_many('posts', ('text', 'author_id'), (('t', 2), ('s', 2)))
        
        user = User.first()
        user.rel('posts').add_many(Post.get()).save()

        user_posts = User.first().posts

        self.assertEqual(len(user_posts), 2)
        self.assertEqual(user_posts[0].text, 't')
        self.assertEqual(user_posts[1].text, 's')

    def test_has_assigning_some(self):
        db.create_many('users', ('username', ), (('t1',), ('t2',)))
        db.create_many('posts', ('text', 'author_id'), (('t', 1), ('s', 2), ('r', 2)))
        
        posts_not_belong_to_1 = Post.where('id', '!=', 1).get()

        user = User.first()
        user.rel('posts').assign_many(posts_not_belong_to_1).save()

        user_posts = User.first().posts

        self.assertEqual(len(user_posts), 2)
        self.assertEqual(user_posts[0].text, 's')
        self.assertEqual(user_posts[1].text, 'r')

    def test_deassigning_all(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('t', 1), ('s', 2)))
        
        user = User.first()
        user.rel('posts').deassign_all().save()

        self.assertEqual(len(User.first().posts), 0)

    def test_has_adding_one(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('t', 2), ('s', 1)))
        
        user = User.first()
        user.rel('posts').add(Post.first()).save()

        user_posts = User.first().posts

        self.assertEqual(len(user_posts), 2)
        self.assertEqual(user_posts[0].text, 't')
        self.assertEqual(user_posts[1].text, 's')
    
    def test_has_one_assignal(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('t', 2), ('s', 1)))

        user = OnePostUser.first()
        user.rel('post').assign(Post.first()).save()

        self.assertEqual(Post.first().author_id, 1)
        self.assertEqual(Post.all()[1].author_id, None)

    def test_has_one_deassignal(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('s', 1),))

        user = OnePostUser.first()
        user.rel('post').deassign().save()
        
        self.assertEqual(Post.first().author_id, None)
        
    def test_belongTo_assignal(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('t', None),))

        first_post = Post.first()
        first_user = User.first()

        first_post.rel('author').assign(first_user)
        first_post.save()

        saved_author = Post.first().author
        self.assertEqual(saved_author.username, 't1')

    def test_belongTo_deassignal(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('t', 1),))

        first_post = Post.first()
        first_post.rel('author').deassign().save()

        self.assertFalse(first_post.author)