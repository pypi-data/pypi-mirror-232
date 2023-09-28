#!/usr/bin/env python
# -*- coding:UTF-8 -*-

"""
@author: fukejie
@file: exponential_det.py
@time: 2023/2/16 10:30
@desc: 
"""

import time

import numpy as np
import torch
from surkit.utils.train import train

from surkit.data.sampling import random_sampler
from surkit.nn.pytorch.fnn import FNN

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
output = ["y"]
max_iteration = 20000
save_path = 'model/model_det.pth'

my_net = FNN(layers, activation, in_d=1, out_d=1, initializer=initializer)
# print(my_net)

train(sampler=sampler, output=output, net=my_net, iterations=max_iteration, target=target,
      optimizer=optimizer, lr=lr, loss_function=loss_function, path=save_path, report_interval=1000)
print(time.time() - start)
