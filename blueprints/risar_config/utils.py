# -*- encoding: utf-8 -*-
from contextlib import contextmanager
import functools
from application.utils import jsonify
from .db import Session


@contextmanager
def session_context(auto_commit=False):
    s = Session()
    try:
        yield s
    except:
        s.rollback()
        raise
    else:
        if auto_commit:
            s.commit()
        else:
            # s.rollback()
            pass


def api_method(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception, e:
            return jsonify({
                'exception': e.__class__.__name__,
                'value': repr(e),
            }, 500, 'Exception')
        else:
            return jsonify(result)
    return wrapper


def api_db_method(auto_commit=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with session_context(auto_commit) as session:
                try:
                    result = func(session, *args, **kwargs)
                except Exception, e:
                    return jsonify({
                        'exception': e.__class__.__name__,
                        'value': repr(e),
                    }, 500, 'Exception')
                else:
                    return jsonify(result)
        return wrapper
    return decorator