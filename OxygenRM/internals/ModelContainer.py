# A container for models
class ModelContainer():
    # An iterator that yields all the rows
    def __iter__(self):
        pass
        
    # Converts all the data to a specified text format
    def to(self):
        pass
        
    # Selects wich fields to select. 
    def select(self):
        pass
        
    # Gets only unique values
    def distinct(self):
        pass
    
    # Sets a order to order records
    def order_by(self):
        pass
        
    # Takes the amount of records specified
    def take(self):
        pass
        
    # Eliminates all the records.
    def delete_all(self):
        pass
        
    # Returns the first record
    def first(self):
        pass
        
    # Filters record by a set criteria
    def filter(self):
        pass
        
    # Specifies a function that will be applied on every record
    def map(self):
        pass
        
    # Limits the number of rows
    def limit(self):
        pass
    
    # Gets all values starting from n
    def offset(self):
        pass
        
    # Sets all the queried records property to a certain value. Will not take effect until it's saved
    def set_all(self):
        pass
        
    # If you modified the records you better save them!!
    def save(self):
        pass    