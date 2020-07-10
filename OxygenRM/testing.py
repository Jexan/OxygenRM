import OxygenRM as O
import OxygenRM.events as event

from functools import wraps, partial

def temporal_events(f):
    """ Decorates a function so it is assured to fire the events (and deactivate the events
        after if they were not active)
    """ 
    @wraps(f)
    def _uses_events(*args, **kwargs):
        deactivate_events = not O.handle_events

        O.use_events()
        result = f(*args, **kwargs)

        if deactivate_events:
            O.cancel_events()

        return result

    return _uses_events

def print_queries(f):
    """ Decorates a function so that all the SQL queries called in it by OxygenRM are
        printed.
    """
    @wraps(f)
    @temporal_events
    def _prints_queries(*args, **kwargs):
        @event.listen('db.operation_perfomed')
        def _(query, values):
            print(query)

        result = f(*args, **kwargs)
        _.times = 0
        return result

    return _prints_queries