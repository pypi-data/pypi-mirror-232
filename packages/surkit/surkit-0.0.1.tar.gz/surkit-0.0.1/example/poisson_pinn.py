#!/usr/bin/env python
# -*- coding:UTF-8 -*-

import os
os.environ['ES_BACKEND'] = 'oneflow'
import numpy as np
import surkit

from matplotlib import pyplot as plt

from surkit.nn import fnn
from surkit.train import train
import surkit.backend as bkd

layers = [64, 64, 64, 64]
activation = "Tanh"
initializer = "He normal"
loss_function = "MSE"
optimizer = "Adam"
lr = 1e-4
x = {"low": -1, "high": 1, "size": (2000, 1)}
input = {"x": x}
output = ["u"]
max_iteration = 10000
save_path = 'model/poisson_%s' % os.environ['ES_BACKEND']

# Dirichlet BC
pde = ["D[u, {x, 2}] = 2"]
icbc = ["u = 0 | x = -1", "u = 4 | x = 1"]

def poisson(xx):
    return (xx + 1) ** 2

# # Neumann BC
# pde = ["D[u, {x, 2}] = 2"]
# icbc = ["u = 0 | x = -1", "D[u, x] = 4 | x = 1"]
#
# def poisson(xx):
#     return (xx + 1) ** 2

# # Robin BC
# pde = ["D[u, {x, 2}] = 2"]
# icbc = ["u = 0 | x = -1", "D[u, x] = u | x = 1"]
#
# def poisson(xx):
#     return (xx + 1) ** 2



net = fnn.FNN(layers, activation, in_d=1, out_d=1, initializer=initializer)

train(input=input, output=output, target=None, constant={}, icbc=icbc, pde=pde, net=net, iterations=max_iteration,
    optimizer=optimizer, lr=lr, loss_function=loss_function, path=save_path, report_interval=1000)


if os.environ['ES_BACKEND'] in ['pytorch', 'oneflow', '']:
    net = bkd.load(save_path).cpu()

    x_in = np.random.uniform(low=-1.0, high=1.0, size=(2000, 1))
    pt_x_in = bkd.np_to_tensor(x_in).float().cpu()

    y = poisson(pt_x_in)
    y_train0 = net(pt_x_in).cpu()

    plt.cla()
    plt.scatter(pt_x_in.detach().numpy(), y.detach().numpy())
    plt.scatter(pt_x_in.detach().numpy(), y_train0.detach().numpy(), c='red')
    plt.show()

if os.environ['ES_BACKEND'] == 'jax':
    import jax
    from flax.training import train_state

    init_key = jax.random.PRNGKey(0)
    params = net.init(init_key, jax.random.uniform(init_key, (1, len(input))))
    state = train_state.TrainState.create(apply_fn=net.apply, params=params, tx=surkit.optimizer.get(optimizer)(learning_rate=lr))
    state = bkd.load(state, save_path)

    x_in = np.random.uniform(low=-1.0, high=1.0, size=(2000, 1))
    pt_x_in = bkd.np_to_tensor(x_in)

    y = poisson(pt_x_in)
    y_train0 = bkd.infer(state, pt_x_in)

    plt.cla()
    plt.scatter(pt_x_in, y)
    plt.scatter(pt_x_in, y_train0, c='red')
    plt.show()