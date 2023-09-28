#!/usr/bin/env python
# -*- coding:UTF-8 -*-

"""
@author: fukejie
@file: navier_stokes_hard_condition.py
@time: 2023/1/17 13:55
@desc: 
"""
import time

import numpy as np
import torch
from surkit.utils.train import train

import surkit.nn.pytorch.fnn
from self_samp import self_d

device = 'cuda' if torch.cuda.is_available() else 'cpu'

print(device)
start = time.time()

layers = [20, 20, 20]
activation = "Swish"
initializer = "He normal"
loss_function = "MSE"
optimizer = "Adam"
lr = 1e-3
eps = 1e-15

x, y, scale = self_d()

sampler = {"x": x, "y": y, "s": scale}
output = ["u", "v", "p"]
max_iteration = 500
save_path = 'model/model3.pth'

pde = [
    "$u$ * $u_x$ + $v$ * $u_y$ - $nu$ * $u__x$ - $nu$ * $u__y$ + $p_x$ / $rho$ = 0",
    "$u$ * $v_x$ + $v$ * $v_y$ - $nu$ * $v__x$ - $nu$ * $v__y$ + $p_y$ / $rho$ = 0",
    "$u_x$ + $v_y$ = 0"
]
icbc = []
hard_condition = ["$h$ = 0.05 - $s$ / sqrt(2 * $pi$ * 0.01) * exp(-1 * ($x$ - 0.5) ** 2 / 0.02)",
                  "$u$ = $u$ * ($h$ ** 2 - $y$ ** 2)",
                  "$v$ = $v$ * ($h$ ** 2 - $y$ ** 2)",
                  "$p$ = 0.1 * (1 - $x$) + (0 - $x$) * (1 - $x$) * $p$"]
constant = {"dp": 0.1, "g": 9.8, "rho": 1, "nu": 1e-3, "L": 1, "pi": np.pi}

my_net = surkit.network.pytorch.fnn.FNN(layers, activation, initializer, in_d=3, out_d=3)
print(my_net)

train(sampler=sampler, output=output, constant=constant, icbc=icbc, pde=pde, net=my_net, iterations=max_iteration,
      report_interval=10, optimizer=optimizer, lr=lr, eps=eps, loss_function=loss_function, path=save_path,
      hard_condition=hard_condition)
print(time.time() - start)
