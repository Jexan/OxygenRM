from OxygenRM.internals.SQL_builders import ColumnData

def default_cols(**cols):
    ''' Create a simple column dictionary with the given arguments.

        Args
            **cols: A list of column_name=column_type.
        
        Returns:
            A dictionary whose keys are the column name and the values a ColumnData tuple. 
    '''
    col_dict = {}
    for col, col_type in cols.items(): 
        col_dict[col] = ColumnData(col_type, False, None, False, False)

    return col_dict