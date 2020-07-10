from collections import namedtuple

ColumnData = namedtuple('ColumnData', 'name type null default primary auto_increment unique check references')

class Column():
    """ The base class for defining a Model (or Migration)
        column.
    """
    def __init__(self, **options):
        object.__setattr__(self, '_set_up', False)
        self.null    = options.get('null', True)
        self.primary = options.get('primary', False)
        self.unique  = options.get('unique', False)
        self.check   = options.get('check', None)
        self.auto_increment = options.get('auto_increment', False)
        self.default = options.get('default', None)
        self.name    = options.get('name', None)
        self.references = options.get('references', None)

        if not self.driver_type:
            self.type = options.get('type', None)

        self.to_be_editted = False
        self.to_be_dropped = False
        
        object.__setattr__(self, '_set_up', True)

    def get_data(self, driver):
        """ Get the relevant data of the column to craft

            Args:
                name: The name of the column to add.
                driver: The driver of the database, as a string.

            Returns:
                A ColumnData tuple.
        """
        type_name = self.driver_type[driver] if self.driver_type else self.type

        return ColumnData(
            self.name, type_name, 
            self.null, self.default, 
            self.primary, self.auto_increment,
            self.unique, self.check, self.references
        )

    @staticmethod
    def from_data(col_data, driver):
        """ Craft a relevant column from the passed ColumnData tuple and db driver.

            Args:
                col_data: A ColumnData tuple with the relevant column info.
                driver: The database driver used (obtained from OxygenRM.db.driver)

            Returns:
                A Column subclass that reflects the passed col_data.

            Notes:
                If the column type has no implemented column class, then the instance will
                be a simple Column.
        """
        return equivalency_dict[driver].get(col_data.type, Column)(**col_data._asdict())

    def __setattr__(self, attr, value):
        if self._set_up:
            object.__setattr__(self, 'to_be_editted', True)
        
        object.__setattr__(self, attr, value)

    def drop(self):
        """ Queue the column to be dropped when the table to which it belongs is saved.
        """
        self.to_be_dropped = True

    """ A dict with the types this column represents
        in various database systems.
    """
    driver_type = {}

class Text(Column):
    """ A basic Text column.
    """
    driver_type = {'sqlite3': 'text'}

class Bool(Column):
    """ A boolean column. Implemented as a small int.

        The possible values to be setted, in a model, are bool, 1 or 0. 
    """
    driver_type = {'sqlite3': 'boolean'}

class Integer(Column):
    """ A basic integer column.
    """
    driver_type = {'sqlite3': 'integer'}
    
class Float(Column):
    """ A basic float column.
    """
    driver_type = {'sqlite3': 'real'}

class Id(Integer):
    """ An auto-incrementing, unsigned integer. Used as a primary key.
    """
    def __init__(self, name='id'):
        data_dict = {
            'name': name,
            'default': None,
            'check': None,
            'unique': True,
            'null': False,
            'primary': True,
            'auto_increment': True
        }

        super().__init__(**data_dict)

equivalency_dict = {
    'sqlite3': {
        'boolean': Bool,
        'integer': Integer,
        'text': Text,
        'float': Float,
    }
}