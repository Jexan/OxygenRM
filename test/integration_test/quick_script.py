from OxygenRM import db_config
from OxygenRM.internals.Table import Table

import OxygenRM.internals.columns as c

db = db_config('sqlite3', ':memory:')

# t = Table('test1_test2')
# t.create_columns(test1_id=c.Integer(), test2_id=c.Integer())  
# t.save()

# t = Table('test1s')
# t.create_columns(id=c.Id())
# t.save()

# t = Table('test2s')
# t.create_columns(id=c.Id())
# t.save()

# db.create_many('test1s', ('id',), ( (i,) for i in range(1, 5)))
# db.create_many('test2s', ('id',), ( (i,) for i in range(1, 5)))

# db.create_many('test1_test2', ('test1_id', 'test2_id'), ((1, i) for i in range(1,4)))

####

t = Table('ts')
t.create_columns(s=c.Text())
t.save()

res = db.execute('INSERT INTO ts (s) VALUES ("yay")')