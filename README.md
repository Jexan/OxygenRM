## OxygenORM

A simple ORM library, made in Python. Supports the creation of Models and Migrations. Uses SQLite, with other databases' support comming in the way.

First we create a database migration:

```
from OxygenRM.migrations import *

class CreateDatabaseAndPosts(Om.Migration):
    def create(self):
        Database('test').create()

        posts = Table('posts')

        posts.create_cols(
            id        = Col.Id(),
            title     = Col.String(),
            body      = Col.Text(null=True),

            timestamps = True
        )

        posts.save()

    def destroy(self):
        Database('test').drop()
```

We run it and then we define a model.

```
import OxygenRM.models as O

class Post(O.Model):
    pass
```

Then, somewhere in your application, just add

```
from OxygenRM import db_config

db_config(driver='sqlite', name='database.db')
```

And you're ready to use your model!

```
import Post
# Creation

Post.craft(title='Hello World', content='A new model!') # Directly

post = Post()
post.title = 'Hello World'
post.content = 'A new model!'
post.save()

# Reading
posts = Post.all()
first_post = posts.first()
first_ten_posts = posts.take(10)

# Updating

Post.find(id=2).update(body='Un modelo nuevo')

post = Post.find(1)
post.title = 'Hola Mundo'
post.save()

# Deleting

Post.find(id=4).destroy(now=True)

post = Post.all().first()
post.destroy()
```

## Relations

To define relations for your model, first, we'll edit the posts table to add a foreign key to an already existing user table.

```
class EditPosts(Om.Migration):
    def __init__(self):
        self.posts_table = Table.get('posts')

    def create(self):      
        self.posts_table.create_cols(author_id = Col.Rel('users'))
        self.posts_table.edit()

    def destroy(self):
        self.posts_table.drop_cols('author_id')
        self.posts_table.edit()
```

And then, in the Post model:

```
import OxygenRM.models as O
import User                       

class Post(O.Model):
    author = O.Belongs('one', User)
```

Meanwhile, in the User model: 

```
import OxygenRM.models as O
import Post                       

class User(O.Model):
    posts = O.Has('many', Post, rel='author_id')
```

You can now access them as you would expect them:

```
import Post

last_post = Post.all().last()
most_recent_author = Post.author.name
```