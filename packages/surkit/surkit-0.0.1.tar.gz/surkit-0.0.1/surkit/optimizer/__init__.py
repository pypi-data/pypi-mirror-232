# # !/usr/bin/env python
# # -*- coding:UTF-8 -*-

import os

from ..backend import backend_name

if os.environ.get("READTHEDOCS") == "True":
    from . import optimizer_pytorch
    from . import optimizer_oneflow
    from . import optimizer_jax


if backend_name == 'pytorch':
    from .optimizer_pytorch import *
elif backend_name == 'oneflow':
    from .optimizer_oneflow import *
elif backend_name == 'jax':
    from .optimizer_jax import *

#
# def _load_backend(mod_name):
#     mod = importlib.import_module(".optimizer_%s" % mod_name, __name__)
#     thismod = sys.modules[__name__]
#     for api, obj in mod.__dict__.items():
#         setattr(thismod, api, obj)
#
#
# _load_backend(backend_name)