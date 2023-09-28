#!/usr/bin/env python
# -*- coding:UTF-8 -*-

"""
@author: fukejie
@file: self_samp.py
@time: 2023/1/17 16:04
@desc: 
"""
from math import sqrt

import numpy as np

from example import mesh_gen


def self_d():
    L = 1
    xStart = 0
    xEnd = xStart + L
    rInlet = 0.05

    nPt = 100
    unique_x = np.linspace(xStart, xEnd, nPt)
    mu = 0.5 * (xEnd - xStart)

    ######################################################

    N_y = 20
    x_2d = np.tile(unique_x, N_y)
    x_2d = np.reshape(x_2d, (len(x_2d), 1))

    ###################################################################

    nu = 1e-3

    ##########
    sigma = 0.1
    ## negative means aneurysm
    scaleStart = -0.02
    scaleEnd = 0
    Ng = 50
    scale_1d = np.linspace(scaleStart, scaleEnd, Ng, endpoint=True)
    x, scale = mesh_gen.ThreeD_mesh(unique_x, x_2d, scale_1d, sigma, mu)

    # axisymetric boundary
    R = scale * 1 / sqrt(2 * np.pi * sigma ** 2) * np.exp(-(x - mu) ** 2 / (2 * sigma ** 2))
    # R = 0

    # Generate stenosis
    yUp = (rInlet - R) * np.ones_like(x)
    yDown = (-rInlet + R) * np.ones_like(x)

    ########################################

    y = np.zeros([len(x), 1])
    for x0 in unique_x:
        index = np.where(x[:, 0] == x0)[0]
        Rsec = max(yUp[index])
        # print('shape of index',index.shape)
        tmpy = np.linspace(-Rsec, Rsec, len(index)).reshape(len(index), -1)
        # print('shape of tmpy',tmpy.shape)
        y[index] = tmpy
    return x, y, scale #, R
