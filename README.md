## OxygenORM

An experimental ORM library, made in Python. Supports the creation of Models and Migrations. Uses SQLite, with other databases' support comming in the way.

Currently at v.0.1. It is properly tested and documented, but you shouldn't use in production just yet.

## Usage:

We define a model:

```
import OxygenRM.models as O

class Post(O.Model):
    id = O.Id()
    title = O.Text()
    text = O.Text()
```

Where every property is named after a field of the table posts. Then, somewhere in your application, just add:

```
from OxygenRM import db_config

db_config(driver='sqlite', name='database.db')
```

And you're ready to use your model!

```
from models import Post
# Creation

Post.craft(title='Hello World', content='A new model!') # Directly

post = Post()
post.title = 'Hello World'
post.content = 'A new model!'
post.save()

post_data = post.to_dict()

# Reading
posts = Post.all()
first_post = posts.first()
first_ten_posts = posts[:10]

post_with_id_1 = posts.find(1)

post.where('title', '=', 'Hello World').or_where('id', '!=', 2)

# Updating

Post.find(2).update(text='Updated')

post = Post.find(1)
post.title = 'Hola Mundo'
post.save()

# Deleting

Post.destroy(4) # deletes post with id 4

post = Post.all().first()
post.delete()


```

Alternatively, if you don't want to create a Model, you can you just generate it based on the database, in one line:

```
import OxygenRM.models as O

Post = O.generate_model_class('posts')

posts = Post.all()
Post.craft(text='Hello World')
```

## QueryBuilder

You can use a lot of conditions for querying, updating and destroying rows, including:

```

Post.where('text', '=', 'Hello World')

Comments.count()

Products.max('price')

User.min('age')

Products.where_in('category', ('phone', 'tv')).sum('price')

Posts.order_by('created_at', 'DESC').limit(10).offset(10).distinct().delete()

User.where_null('email').first_or_fail()

# You can call the query in two ways:

# 1
Posts.where('text', 'LIKE', '%Hello%').get()

# 2
for post in Posts.where('text', 'LIKE', '%Hello%'):
    print(post)

# Chaining

Products.where('price', '>', 200).or_where('category', '=', 'phones').and_where('brand', '=', 'Samsung')

```

## ModelContainer

Every query that could fetch more than one row (e.g., Post.get(), Post.all()) will return a ModelContainer collection. The ModelContainer has many useful methods for handling your row models after fetching them:

```
products = Product.all()

# It's handled exactly like python lists

last_product = products[-1]
amount_products = len(products)
odd_id_products = products[::2]

# Get one

products.first()
products.first_or_fail()

# Filter or find in the collection

products.find(lambda product: product.id == 1)
products.filter(lambda product: product.category == 'phone')

# Get the list of values of just one fields

all_categories = set(products.pluck('price'))

# Serialize it or print it nicely

products.to_dict()
products.pretty() == str(products)
products.to_json()

```

## Relations

To define relations for your model, we'll assume that the Post table has an author_id field:  

```
import OxygenRM.models as O
from .User import User                       

class Post(O.Model):
    @classmethod
    def relations(cls):
        cls.author = O.BelongsTo('one', User)
```

Meanwhile, in the User model: 

```
import OxygenRM.models as O
from .Post import Post                       

class User(O.Model):
    @classmethod
    def relations(cls):
        cls.posts = O.Has('many', Post, rel='author_id')
```

You can now access them as you would expect:

```
last_post = Post.all().last()
most_recent_author = Post.author.name

# The "Many" field allows you to use query building:

author = User.find(1)

posts_with_hello_by_author = author.posts.where('text', '=', 'hello').get()

# Relating and unrelating models is quite easy

post = Post.find(2)
post.author.assign(User.first()).save()
post.author.deassign().save()

# A HasMany has more variety

user = User.first()

user.posts.add(Post.order_by('id').first()).save()
user.posts.deassign(Post.order_by('id').first()).save()

user.posts.deassign_all().save()
```

Many To Many relations are made with Multiple.

```
import OxygenRM.models as O

class Post(O.Model):
    text = O.Text()
    id = O.Id()

    @classmethod
    def relations(cls):
        cls.readed_by = O.Multiple(User)

class User(O.Model):
    id = O.Id()
    username = O.Text()
    
    # You don't need to define the relation in the relations method if there related class has already been defined.
    read_posts = O.Multiple(Post) 
```

To add and remove, use the same methods of "hasMany" fields.

## More

There's more features, like ManyToMany's fields pivots, creation of tables, database events, special model fields (like Pickle and JSON) and (coming soon) migration handling. 

However, these are still experimental and may change their implementation.

## About

This project was born due to the lack of simplicity of other Python ORMs. I wanted an alternative that was cleaner and quicker.

All of this was created by a single person (so far). It was an herculean task, but most of the basic, fundamental things are done. 

If you want to contribute to this project, don't hesitate to send me an email to JeanFGomezR@gmail.com.
