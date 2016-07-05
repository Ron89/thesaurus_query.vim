# -*- coding: utf-8 -*-
#
# load all backend modules
import os as _os
__all__=[]
for backend in _os.listdir(_os.path.dirname(__file__)):
    if 'lookup' in backend and backend[-3:] == '.py':
        __all__.append(backend[:-3])

from . import *

query_backends = dict()
_local_namespace = locals()
for backend in __all__:
    query_backends[_local_namespace[backend].identifier] = \
        _local_namespace[backend]

del _local_namespace
