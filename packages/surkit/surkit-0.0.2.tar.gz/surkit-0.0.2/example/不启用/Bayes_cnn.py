#!/usr/bin/env python
# -*- coding:UTF-8 -*-

"""
@author: fukejie
@file: Bayes_cnn.py
@time: 2023/2/20 15:41
@desc: 
"""

import h5py
import torch
from surkit.nn.dense_ed import DenseED
from surkit.utils.train import train2d
from torch.utils.data import DataLoader, TensorDataset

device = 'cuda' if torch.cuda.is_available() else 'cpu'

blocks = [6, 8, 6]
net = DenseED(in_channels=1, out_channels=3, imsize=64, blocks=blocks)

activation = "Tanh"
initializer = "He normal"


# print(a)
#
# test_img = torch.zeros([1, 1, 64, 64])
# print(a(test_img).shape)


def load_data(hdf5_file, ndata, batch_size, only_input=True, return_stats=False):
    with h5py.File(hdf5_file, 'r') as f:
        x_data = f['input'][:ndata]
        # print(f'x_data: {x_data.shape}')
        if not only_input:
            y_data = f['output'][:ndata]
            # print(f'y_data: {y_data.shape}')

    stats = {}
    if return_stats:
        y_variation = ((y_data - y_data.mean(0, keepdims=True)) ** 2).sum(
            axis=(0, 2, 3))
        stats['y_variation'] = y_variation

    data_tuple = (torch.FloatTensor(x_data),) if only_input else (
        torch.FloatTensor(x_data), torch.FloatTensor(y_data))
    data_loader = DataLoader(TensorDataset(*data_tuple),
                             batch_size=batch_size, shuffle=True, drop_last=True, generator=torch.Generator(device = 'cuda'))
    # print(f'Loaded dataset: {hdf5_file}')
    return data_loader, stats


data_dir = "../example/datasets"

ntrain = 4096
ntest = 512

train_hdf5_file = data_dir + f'/{64}x{64}/kle512_lhs10000_train.hdf5'

train_loader, _ = load_data(train_hdf5_file, ntrain, 32,
                            only_input=True, return_stats=False)

test_hdf5_file = data_dir + f'/{64}x{64}/kle512_lhs1000_val.hdf5'
ntrain_total, ntest_total = 10000, 1000

test_loader, test_stats = load_data(test_hdf5_file, 512,
                                    64, only_input=False, return_stats=True)

sampler = {"k": train_loader}

output = ["p", "ux", "uy"]
pde = ["$ux$ = -$k$ * $p_k.h$", "$uy$ = -$k$ * $p_k.v$", "$ux_k.h$ + $uy_k.v$ = 0"]
icbc = ["$p_left$ = 1", "$p_right$ = 0", "$uy_top$ = 0", "$uy_down$ = 0"]

train2d(sampler=train_loader, inputs=['k'], constant={}, output=output, icbc=icbc, pde=pde, iterations=300,
        device=device, boundary_weight=10.,
        loss_function="MSE", lr=1e-3, net=net, path='./1model4.pth', optimizer="Adam", report_interval=10, imsize=64)
