#!/usr/bin/env python
# -*- coding:UTF-8 -*-

"""
@author: fukejie
@file: 123.py
@time: 2023/3/9 13:44
@desc: 
"""

import time

import numpy as np
import torch
from surkit.utils.train import train

import surkit.nn.pytorch.fnn

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(device)
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
save_path = 'model/model_mo.pth'
pde = ["$y$ = $y__x$"]
icbc = ["$y$ = 1 @ $x$ = 0", "$y$ = $e$ @ $x$ = 2"]
constant = {"e": np.exp(2)}
transforms = ['sin', 'cos', 'pow2', 'exp']

my_net = surkit.network.pytorch.fnn.FNN(layers, activation, initializer, in_d=1, out_d=1, excitation="unfixed")
# print(my_net)

train(sampler=sampler, output=output, constant=constant, icbc=icbc, pde=pde, net=my_net, iterations=max_iteration,
      optimizer=optimizer, lr=lr, loss_function=loss_function, path=save_path, device=device, report_interval=1000)
print(time.time() - start)
