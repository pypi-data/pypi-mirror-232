#!/usr/bin/env python
# -*- coding:UTF-8 -*-

"""
@author: fukejie
@file: bayes_cnn_demo.py
@time: 2023/3/6 14:36
@desc: 
"""
import os

import torch

os.environ["TL_BACKEND"]="pytorch"
from surkit.losses import elbo
from surkit.nn.pytorch.bayes_cnn import BayesCnn


def main():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    con_dict1 = {"type": "conv", "out_channel": 32, "size": 5, "stride": 1, "padding": 2, "bias": True}
    con_dict2 = {"type": "activation", "name": "sigmoid"}
    con_dict21 = {"type": "pooling", "name": "max", "size": 5, "stride": 1, "padding": 2, "bias": True}
    con_dict32 = {"type": "bn"}
    con_dict3 = {"type": "transconv", "out_channel": 64, "size": 5, "stride": 1, "padding": 0, "output_padding": 0, "bias": True}
    con_dict4 = {"type": "activation", "name": "sigmoid"}
    con_dict5 = {"type": "flatten"}
    con_dict6 = {"type": "fc", "out_d": 10}
    con_dict7 = {"type": "activation", "name": "sigmoid"}

    a = BayesCnn([con_dict1, con_dict2, con_dict21, con_dict32, con_dict3, con_dict4, con_dict5, con_dict6, con_dict7],
                 [32, 32], 1, 1, 10).to(device)
    i = torch.zeros((12, 1, 32, 32)).to(device)
    y = torch.zeros((12, 1)).to(device)
    optimizer = torch.optim.Adam(a.parameters(), lr=0.1)

    for epoch in range(1000):  # loop over the dataset multiple times
        optimizer.zero_grad()
        # forward + backward + optimize
        loss = elbo(i, y, 1, a)
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 100 == 0:
            print('epoch: {}/{}'.format(epoch + 1, 1000))
            print('Loss:', loss.item())
    print('Finished Training')


if __name__ == '__main__':
    main()
