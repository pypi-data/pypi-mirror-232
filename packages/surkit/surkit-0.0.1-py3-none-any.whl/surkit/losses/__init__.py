#!/usr/bin/env python
# -*- coding:UTF-8 -*-

# def get(loss_function, reduction='mean'):
#     pass
#
def elbo(x, y, samples, net):
    pass

import importlib
import os
import sys

from ..backend import backend_name

if os.environ.get("READTHEDOCS") == "True":
    from . import losses_pytorch
    from . import losses_oneflow
    from . import losses_jax


def _load_backend(mod_name):
    mod = importlib.import_module(".losses_%s" % mod_name, __name__)
    thismod = sys.modules[__name__]
    for api, obj in mod.__dict__.items():
        setattr(thismod, api, obj)


_load_backend(backend_name)
