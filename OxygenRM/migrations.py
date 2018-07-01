import OxygenRM.internals.columns as Col
import OxygenRM.internals.Table   as Table

# Abstract base class for migrations 
class Migration():
    def call(self):
        pass

def set_from_last_migration():
    pass

class Database():
    def __init__(self, name):
        pass