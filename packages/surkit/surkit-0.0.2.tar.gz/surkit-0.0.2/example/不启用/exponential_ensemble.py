#!/usr/bin/env python
# -*- coding:UTF-8 -*-

"""
@author: fukejie
@file: exponential_ensemble.py
@time: 2023/3/13 16:18
@desc: 
"""


import time

import numpy as np
import torch
from surkit.utils.train import train_gaussian

from surkit.data.sampling import random_sampler
from surkit.nn.pytorch.nn_ensemble import MixtureNN

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(device)
start = time.time()

layers = [20, 20]
activation = "Tanh"
initializer = "He normal"
loss_function = "MSE"
optimizer = "Adam"
lr = 1e-4
x = random_sampler(0, 2, (2000, 1))
y = np.exp(x)
sampler = {"x": x}
target = {"y": y}
output = ["y"]
max_iteration = 20000
save_path = 'model/model_ensemble.pth'

my_net = MixtureNN(5, layers, activation, in_d=1, out_d=1, initializer=initializer)
print(my_net)

train_gaussian(sampler=sampler, output=output, net=my_net, iterations=max_iteration, target=target,
               optimizer=optimizer, lr=lr, path=save_path, report_interval=1000)
print(time.time() - start)
