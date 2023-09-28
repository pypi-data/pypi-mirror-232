#!/usr/bin/env python
# -*- coding:UTF-8 -*-

"""
@author: fukejie
@file: exponential_bayes.py
@time: 2023/2/15 14:40
@desc: 
"""

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.optim as optim

from surkit.data.sampling import random_sampler
from surkit.losses.losses_pytorch import elbo
from surkit.nn.pytorch.bayes_nn import BayesNN


# matplotlib.use('TkAgg')


def main():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def toy_function(x):
        return torch.exp(x)

    x = torch.tensor(random_sampler(0, 2, (2000, 1))).float().to(device)
    y = toy_function(x)
    layers = [20, 20, 20]
    activation = "sigmoid"
    net = BayesNN(layers, activation, in_d=1, out_d=1, prior_var=0.1).to(device)
    optimizer = optim.Adam(net.parameters(), lr=0.1)
    epochs = 20000
    best_loss = float('inf')
    for epoch in range(epochs):  # loop over the dataset multiple times
        optimizer.zero_grad()
        # forward + backward + optimize
        loss = elbo(x, y, 4, net)
        loss.backward()
        optimizer.step()
        if (epoch + 1) % 100 == 0:
            print('epoch: {}/{}'.format(epoch + 1, epochs))
            print('Loss:', loss.item())
            if loss < best_loss:
                best_loss = loss
                torch.save(net, "model/bnn1")
                print("bnn1 saved")
    print('Finished Training')

    # samples is the number of "predictions" we make for 1 x-value.
    samples = 100
    x_tmp = torch.linspace(-2, 4, 1000).reshape(-1, 1).to(device)
    y_samp = np.zeros((samples, 1000))
    net = torch.load("model/bnn1")
    for s in range(samples):
        y_tmp = net(x_tmp).cpu().detach().numpy()
        y_samp[s] = y_tmp.reshape(-1)
    plt.plot(x_tmp.cpu().numpy(), np.mean(y_samp, axis=0), label='Mean Posterior Predictive')
    plt.fill_between(x_tmp.cpu().numpy().reshape(-1), np.percentile(y_samp, 2.5, axis=0),
                     np.percentile(y_samp, 97.5, axis=0),
                     alpha=0.25, label='95% Confidence')
    plt.legend()
    plt.scatter(x.cpu(), y.cpu())
    plt.title('Posterior Predictive')
    plt.show()


if __name__ == '__main__':
    main()
