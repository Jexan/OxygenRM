import OxygenRM as O
import OxygenRM.events as event

from functools import wraps, partial

def temporal_events(f):
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