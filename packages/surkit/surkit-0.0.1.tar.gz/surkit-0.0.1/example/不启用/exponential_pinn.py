#!/usr/bin/env python
# -*- coding:UTF-8 -*-

"""
@author: fukejie
@file: exponential_pinn.py
@time: 2023/1/6 9:55
@desc: 
"""
import time

import numpy as np
from surkit.utils.train import train

import surkit.nn as nn

start = time.time()

layers = [20, 20, 20]
activation = "Tanh"
initializer = "He normal"
loss_function = "MSE"
optimizer = "Adam"
lr = 1e-4
sampler = {"x": {"low": 0, "high": 2, "size": (2000, 1)}}
output = ["y"]
max_iteration = 20000
save_path = 'model/model_pinn.pth'
pde = ["$y$ = $y__x$"]
icbc = ["$y$ = 1 @ $x$ = 0", "$y$ = $e$ @ $x$ = 2"]
constant = {"e": np.exp(2)}
transforms = ['sin', 'cos', 'pow2', 'exp']

my_net = nn.fnn.FNN(layers=layers, activation=activation, initializer=initializer, in_d=1, out_d=1)
# print(my_net)

train(sampler=sampler, output=output, constant=constant, icbc=icbc, pde=pde, net=my_net, iterations=max_iteration,
      optimizer=optimizer, lr=lr, loss_function=loss_function, path=save_path, report_interval=1000)
print(time.time() - start)
