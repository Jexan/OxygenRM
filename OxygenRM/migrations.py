import OxygenRM.internals.columns as Col
import OxygenRM.internals.Table   as Table

# Abstract base class for migrations 
class Migration():
    # When applied
    def create():
        pass
            
    # When dissapplied
    def destroy():
        pass

def set_from_last_migration():
    pass

class Database():
    def __init__(self, name):
        pass