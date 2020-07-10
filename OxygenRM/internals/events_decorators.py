from functools import wraps
from math import inf

EVENTS = None


def operation_perfomed(f, times=inf):
    f.times = times
    EVENTS['db.operation_perfomed'].append(f)

    return f

def created_record(f, times=inf):
    f.times = times
    EVENTS['db.created_record'].append(f)

    return f

def operation_called(f, times=inf):
    f.times = times
    EVENTS['db.operation_called'].append(f)

    return f