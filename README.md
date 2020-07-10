## OxygenORM

A simple ORM library, made in Python. Supports the creation of Models and Migrations. Uses SQLite, with other databases' support comming in the way.

We define a model:

```
import OxygenRM.models as O

class Post(O.Model):
    id = O.Id()
    title = O.Text()
    body = O.Text()
```

Then, somewhere in your application, just add,

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
first_ten_posts = posts[:10]

# Updating

Post.find(id=2).update(body='Un modelo nuevo')

post = Post.find(1)
post.title = 'Hola Mundo'
post.save()

# Deleting

Post.destroy(4)

post = Post.all().first()
post.delete()
```

## Relations

To define relations for your model, we'll assume that the Post table has an author_id field:  

```
import OxygenRM.models as O
import User                       

class Post(O.Model):
    @classmethod
    def relations(cls):
        cls.author = O.BelongsTo('one', User)
```

Meanwhile, in the User model: 

```
import OxygenRM.models as O
import Post                       

class User(O.Model):
    @classmethod
    def relations(cls):
        cls.posts = O.Has('many', Post, rel='author_id')
```

You can now access them as you would expect them:

```
import Post

last_post = Post.all().last()
most_recent_author = Post.author.name
```