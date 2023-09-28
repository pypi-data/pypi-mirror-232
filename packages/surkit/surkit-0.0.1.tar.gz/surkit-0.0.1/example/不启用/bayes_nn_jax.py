#!/usr/bin/env python
# -*- coding:UTF-8 -*-

import os

import jax
import optax
from flax.training import train_state

os.environ["ES_BACKEND"]="jax"

import numpy as np

import surkit.nn.jax.bayes_nn as nn
import time
start = time.time()
import matplotlib.pyplot as plt

from surkit.data.sampling import random_sampler
from surkit.losses.losses_jax import elbo


# matplotlib.use('TkAgg')


def main():

    def toy_function(x):
        return np.exp(x)

    x = random_sampler(0, 2, (2000, 1))
    y = toy_function(x)
    layers = [64, 64]
    activation = "sigmoid"
    net = nn.BayesNN(layers, activation, in_d=1, out_d=1, prior_var=0.1)
    optimizer = optax.adam(learning_rate=0.1)
    key, init_key = jax.random.split(jax.random.PRNGKey(0))
    params = net.init(init_key, jax.random.uniform(init_key, (1, 1)))
    state = train_state.TrainState.create(apply_fn=net.apply, params=params, tx=optimizer)
    # print(state.params)

    def loss_fn(params_):
        return elbo(x, y, 64, net, params_)

    @jax.jit
    def jit_train_step(state_):
        loss_, grads = (jax.value_and_grad(loss_fn))(state_.params)
        new_state = state_.apply_gradients(grads=grads)
        return new_state, loss_

    epochs = 2000
    best_loss = float('inf')
    for epoch in range(epochs):  # loop over the dataset multiple times
        state, loss = jit_train_step(state)
        if (epoch + 1) % 100 == 0:
            # print('epoch: {}/{}'.format(epoch + 1, epochs))
            # print('Loss:', loss.item())
            if loss < best_loss:
                best_loss = loss
                best_state = state
                print('Loss:', loss.item())
                print("bnn1 saved")
    print('Finished Training')
    # print(state.params)
    state=best_state
    # samples is the number of "predictions" we make for 1 x-value.
    samples = 100
    x_tmp = np.linspace(-2, 4, 1000).reshape(-1, 1)
    y_samp = np.zeros((samples, 1000))
    for s in range(samples):
        y_tmp = state.apply_fn(state.params, x_tmp)
        y_samp[s] = y_tmp.reshape(-1)
    plt.plot(x_tmp, np.mean(y_samp, axis=0), label='Mean Posterior Predictive')
    plt.fill_between(x_tmp.reshape(-1), np.percentile(y_samp, 2.5, axis=0),
                     np.percentile(y_samp, 97.5, axis=0),
                     alpha=0.25, label='95% Confidence')
    plt.legend()
    plt.scatter(x_tmp, toy_function(x_tmp))
    plt.title('Posterior Predictive')
    plt.show()
    # print(x_tmp)
    # print(np.mean(y_samp, axis=0))

if __name__ == '__main__':
    main()

print(time.time() - start)

