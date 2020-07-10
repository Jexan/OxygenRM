from collections import defaultdict
from functools import wraps, partial
from math import inf
import OxygenRM

""" A dictionary whose keys are the events names and the values a list
    of functions to be called when the event is fired.
"""
EVENTS = defaultdict(list)

"""
"""
HANDLERS = {}

""" The name of the last event fired
"""
last_fired = None

def operation_called_handler(f, *args):
    if len(args) == 1:
        return f(args[0], ())
    else:
        return f(*args)

HANDLERS['db.operation_called'] = operation_called_handler 
HANDLERS['db.operation_perfomed'] = operation_called_handler 

def listen(event, times=inf):
    """ Decorate a function so it is called when the given event is fired  

        Args:
            event: A string name of events
            times: The amount of times the event will fire. Default is infinity
    """
    def decorator(f):
        if event in HANDLERS:
            f = partial(HANDLERS[event], f)
        
        f.times = times
        EVENTS[event].append(f)

        return f

    return decorator

def drop_all_events():
    """ Stops all events' caller
    """
    for key in tuple(EVENTS.keys()):
        del EVENTS[key]

def fire(event, *args, **kwargs):
    """ Fire an event and passes the given arguments to the listening functions.

        Args:
            event: The event name to fire
            *args, **kwargs
    """
    if OxygenRM.handle_events:
        global last_fired
        last_fired = event

        for i in tuple(EVENTS[event]):
            if i.times:
                i(*args, **kwargs)
                i.times -= 1 
            else:
                EVENTS[event].remove(i)

def fires_after(event):
    """ Decorates the function so that the event will fire after the function is called,
        with the function arguments.

        Args:
            event: The event name
    """
    def decorator(f):
        @wraps(f)
        def wrapped_f(instance, *args, **kwargs):
            result = f(instance, *args, **kwargs)
            fire(event, *args, **kwargs)

            return result

        return wrapped_f
    return decorator

def fires_before(event):
    """ Decorates the function so that the event will fire before the function is called,
        with the function arguments.

        Args:
            event: The event name
    """
    def decorator(f):
        @wraps(f)
        def wrapped_f(instance, *args, **kwargs):
            fire(event, *args, **kwargs)
            return f(instance, *args, **kwargs)

        return wrapped_f
    return decorator