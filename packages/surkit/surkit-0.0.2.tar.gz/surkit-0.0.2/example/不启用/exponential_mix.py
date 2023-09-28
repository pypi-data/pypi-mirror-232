#!/usr/bin/env python
# -*- coding:UTF-8 -*-

"""
@author: fukejie
@file: exponential_mix.py
@time: 2023/2/16 12:39
@desc: 
"""

import time

import numpy as np
import torch
from surkit.utils.train import train

import surkit.nn.pytorch.fnn
from surkit.data.sampling import random_sampler

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(device)
start = time.time()

layers = [20, 20, 20]
activation = "Tanh"
initializer = "He normal"
loss_function = "MSE"
optimizer = "Adam"
lr = 1e-4
x = random_sampler(0, 2, (2000, 1))
y = np.exp(x)
sampler = {"x": x}
target = {"y": y}
pde = ["$y$ = $y__x$"]
icbc = ["$y$ = 1 @ $x$ = 0", "$y$ = $e$ @ $x$ = 2"]
constant = {"e": np.exp(2)}
output = ["y"]
max_iteration = 20000
save_path = 'model/model_mix.pth'

my_net = surkit.network.pytorch.fnn.FNN(layers, activation, in_d=1, out_d=1, initializer=initializer)
# print(my_net)

train(sampler=sampler, output=output, net=my_net, iterations=max_iteration, target=target, pde=pde, icbc=icbc,
      constant=constant,
      optimizer=optimizer, lr=lr, loss_function=loss_function, path=save_path, report_interval=1000)
print(time.time() - start)
