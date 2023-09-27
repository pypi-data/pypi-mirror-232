# #! /usr/bin/python
# # -*- coding: utf-8 -*-

import json
import os
import sys

backend_name = None

config_path = os.path.join(os.path.expanduser("~"), ".easy_surrogate", "config.json")

# Set backend based on ES_BACKEND.
if 'ES_BACKEND' in os.environ:
    backend = os.environ['ES_BACKEND']
    if backend:
        backend_name = backend
# Set backend based on config.
elif os.path.exists(config_path):
    with open(config_path, "r") as config_file:
        config_dict = json.load(config_file)
        backend_name = config_dict.get("backend", "").lower()

# import backend functions
if backend_name in ['pytorch', None]:
    if not backend_name:
        print("Backend not selected, use default backend.")
        backend_name = 'pytorch'
    from .pytorch_bkd import *
    import torch
    BACKEND_VERSION = torch.__version__
    sys.stdout.write('Using PyTorch backend.\n')

elif backend_name == 'oneflow':
    from .oneflow_bkd import *
    import oneflow as flow
    BACKEND_VERSION = flow.__version__
    sys.stdout.write('Using OneFlow backend.\n')

elif backend_name == 'jax':
    from .jax_bkd import *
    import jax
    BACKEND_VERSION = jax.__version__
    sys.stdout.write('Using JAX backend.\n')
else:
    raise NotImplementedError("Backend %s is not supported" % backend_name)
