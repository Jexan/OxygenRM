# Dependency Loading

import unittest

from OxygenRM import db
from OxygenRM.internals.ModelContainer import ModelContainer
from OxygenRM.internals.Table import Table
import OxygenRM.internals.columns as c

from ..internals_test import default_cols

import OxygenRM.models as O

from OxygenRM.internals.fields import *

id_col = next(default_cols(id='integer'))._replace(primary=True, auto_increment=True)