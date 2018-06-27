# Allows the creation, edition and droppage of tables
class Table():
    # If the table already exists, grabs it. If not, it creates one.
    def __init__(self, table_name):
        pass

    # Allows adding columns to a table
    def create_cols(self, **kwargs):
        pass

    def rename(self, name):
        pass

    def drop_cols(self, *args):
        pass

    def rename_cols(self, **kwargs):
        pass

    def edit_cols_props(self, **kwargs):
        pass  

    def destroy(self):
        pass

    def edit(self):
        pass

    def create(self):
        pass