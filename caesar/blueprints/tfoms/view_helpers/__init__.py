# -*- encoding: utf-8 -*-
from ..app import _config


if _config('region_code') == 'pnz':
    from .pnz import *
elif _config('region_code') == 'spb':
    from .spb import *
else:
    raise ImportError(u'Cannot import views for {0}'.format(_config('region_code')))
