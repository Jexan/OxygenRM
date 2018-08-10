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

user_cols = [
    next(default_cols(id='integer'))._replace(primary=True, auto_increment=True),
    next(default_cols(username='text'))
]

post_cols = [
    next(default_cols(id='integer'))._replace(primary=True, auto_increment=True),
] + list(default_cols(text='text', author_id='integer'))

User.set_up()
Post.set_up()
OnePostUser.set_up()

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
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('t', 1),))

        user_post = User.first().posts
        self.assertIsInstance(user_post, QueryBuilder)

        bullshit_i_have_to_do_because_the_test_are_fucking_broken = user_post.first()
        pure_post = Post.first()
        self.assertEqual(bullshit_i_have_to_do_because_the_test_are_fucking_broken, pure_post)

    def test_that_models_has_key_access_is_not_broken_on_simple_methods(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('t', 1),))

        def get_text(model):
            return model.text

        posts = User.first().posts.get()
        self.assertEqual('t', get_text(posts[0]))

    def test_has_with_no_result_queries_empty(self):
        db.create('users', username='t1')

        user_post = User.first().posts

        self.assertEqual(len(user_post.get()), 0)

    def test_has_queries_correctly_with_multiple_related_model(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('t', 1), ('s', 1), ('r', 1)))

        user_posts = User.first().posts.get()

        self.assertEqual(len(user_posts), 3)
        self.assertEqual(user_posts[2].text, 'r')
        self.assertEqual(user_posts[1].text, 's')

    def test_has_queries_correctly_even_with_other_unrelated_models_present(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('t', 1), ('s', 2)))

        user_posts = User.first().posts.get()

        self.assertEqual(len(user_posts), 1)
        self.assertEqual(user_posts.first().text, 't') 

    def test_has_assigning_one(self):
        db.create('users', username='t1')
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

    def test_has_assigning_some(self):
        db.create_many('users', ('username', ), (('t1',), ('t2',)))
        db.create_many('posts', ('text', 'author_id'), (('t', 1), ('s', 2), ('r', 2)))
        
        posts_not_belong_to_1 = Post.where('id', '!=', 1).get()

        user = User.get()[0]
        user.posts.assign_many(posts_not_belong_to_1)
        user.save()

        user_posts = User.get()[0].posts.get()

        self.assertEqual(len(user_posts), 2)
        self.assertEqual(user_posts[0].text, 's')
        self.assertEqual(user_posts[1].text, 'r')

    def test_deassigning_all(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('t', 1), ('s', 2)))
        
        user = User.first()
        user.posts.deassign_all()
        user.save()

        user_posts = User.get()[0].posts.get()

        self.assertEqual(len(user_posts), 0)

    def test_has_adding_one(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('t', 2), ('s', 1)))
        user = User.first()
        user.posts.add(Post.first())
        user.save()

        user_posts = User.first().posts.get()

        self.assertEqual(len(user_posts), 2)
        self.assertEqual(user_posts[0].text, 't')
        self.assertEqual(user_posts[1].text, 's')

    def test_has_one_works(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('s', 1),))

        post = OnePostUser.first().post

        self.assertIsInstance(post, Post)
    
    def test_has_one_assignal(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('t', 2), ('s', 1)))

        user = OnePostUser.first()
        post = user.post

        post.assign(Post.first())
        user.save()

        self.assertEqual(Post.first().author_id, 1)
        self.assertEqual(Post.get()[1].author_id, None)

    def test_has_one_deassignal(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('s', 1),))

        user = OnePostUser.first()
        post = user.post

        post.deassign()
        
        user.save()
        self.assertEqual(Post.first().author_id, None)
        
    # Belongs To!
    def test_belongsTo_queries_correctly_with_one_related_model(self):
        db.create('users', username='t1')
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

        self.assertFalse(post_author)

    def test_belongTo_assignal(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('t', None),))

        first_post = Post.first()
        first_user = User.first()

        first_post.author.assign(first_user)
        first_post.save()

        saved_author = Post.first().author
        self.assertEqual(saved_author.username, 't1')

    def test_belongTo_deassignal(self):
        db.create('users', username='t1')
        db.create_many('posts', ('text', 'author_id'), (('t', 1),))

        first_post = Post.first()
        first_post.author.deassign().save()

        self.assertFalse(first_post.author)