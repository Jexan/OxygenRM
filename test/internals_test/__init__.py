from OxygenRM.internals.SQL_builders import ColumnData

def default_cols(**cols):
    """ Create a simple column dictionary with the given arguments.

        Args
            **cols: A list of column_name=column_type.
        
        Yield:
            ColumnData tuples
    """
    for col_name, col_type in cols.items(): 
        yield ColumnData(
            col_name, col_type, 
            null=True, default=None, 
            primary=False, auto_increment=False, 
            unique=False, check=None, references=None
        )