# -*- encoding: utf-8 -*-
from nemesis.app import app
from ..app import _config

with app.app_context():
    if _config('region_code') == 'pnz':
        from .pnz import *
    elif _config('region_code') == 'spb':
        from .spb import *
    else:
        pass
        # raise ImportError(u'Cannot import views for {0}'.format(_config('region_code')))
