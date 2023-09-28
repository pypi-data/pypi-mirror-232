#!/usr/bin/env python
# -*- coding:UTF-8 -*-

"""
@author: fukejie
@file: exponential_pinn_args.py.py
@time: 2023/3/15 15:25
@desc: 
"""


import argparse
import time

import numpy as np
from surkit.utils.train import train

from surkit.data import sampling
from surkit.nn.pytorch.fnn import FNN
from surkit.utils.parse import parse_dict

pi = np.pi
exp = np.exp
log = np.log

def parse():
    parser = argparse.ArgumentParser(
        description="This is a quick and easy script to build a surrogate model based on "
                    "the configuration",
        usage="python %(prog)s []",
        # epilog='暂无额外信息。'
    )

    # model parameter
    parser.add_argument('--activation', choices=['swish', 'relu', 'leaky_relu', 'tanh', 'sigmoid'], default='tanh',
                        help='the activation function used in NN')
    parser.add_argument('--initializer', choices=['xavier uniform', 'xavier normal', 'he uniform', 'he normal'],
                        default='he normal', help='the initializer used in NN')
    parser.add_argument('--layers', nargs='+', type=int, help='the number of neurons in each layer. i.e. 20 20 20',
                        required=True)
    parser.add_argument('--transforms', nargs='+', type=str, help='affine layer of the nn. i.e. exp, sin, cos, pow2')
    parser.add_argument('--excitation', choices=['fixed', 'unfixed'], default=None, help='excitation block mode')

    # training parameter
    parser.add_argument('--device', choices=['cuda', 'cpu'], default='cuda', help='the device tensor computes in')
    parser.add_argument('--loss_function', choices=['mae', 'mse'], default='mse',
                        help='the loss function used in training')
    parser.add_argument('--optimizer', choices=['adam', 'LBFGS'], default='adam',
                        help='the optimizer used in training')
    parser.add_argument('--lr', type=float, default=1e-4, help='the learning rate of the optimizer')
    parser.add_argument('--max_iteration', type=int, default=20000, help='the max iteration steps in training')
    parser.add_argument('--report_interval', type=int, default=1000, help='report frequency')
    # pinn
    parser.add_argument('--pde', nargs='+', type=str, default=None,
                        help='partial differential equation, the variable name is wrapped in $$ and the number of _s '
                             'represents the number of order derivatives, i.e. $y__x$')
    parser.add_argument('--icbc', nargs='+', type=str, default=None,
                        help='definite condition, the variable name is wrapped in $$$ and the number of _s represents'
                             ' the number of order derivatives, @ followed by the boundary or initial value, '
                             'i.e. $y$ = 1 @ $x$ = 0"')
    parser.add_argument('--constant', type=parse_dict, help="constant used in calculation")

    # save parameter
    parser.add_argument('--save_path', type=str, default='.', help='the save path of model')
    # parser.add_argument('--output_path', type=str, default='.', help='the output path of model')

    # data parameter
    parser.add_argument('--train_set', type=str, default=None, help='the train set path')
    parser.add_argument('--train_set_target', type=str, default=None, help='the train set target path')
    parser.add_argument('--val_set', type=str, default=None, help='the validation set path')
    parser.add_argument('--val_set_target', type=str, default=None, help='the validation set target path')
    parser.add_argument('--test_set', type=str, default=None, help='the test set path')
    parser.add_argument('--test_set_target', type=str, default=None, help='the test set target path')

    parser.add_argument('--repeat_sample', action='store_true', help='whether the data is required to be sampled '
                                                                     'repeatedly each round')
    parser.add_argument('--sampler', nargs='+', type=parse_dict, help="list of dictionary with sampler parameter "
                                                                      "i.e. {'mode':'random', 'name': 'x', 'low':0, "
                                                                      "'high':2, 'size':(2000, 1)}")
    parser.add_argument('--output_name', nargs='+', type=str, required=True)

    return parser


def main():
    a = parse()
    args = a.parse_args()
    start = time.time()
    sampler = {}
    # target = {}
    if args.sampler:
        if args.repeat_sample:
            for s in args.sampler:
                name = s.pop("name")
                sampler[name] = s
        else:
            for s in args.sampler:
                name = s.pop("name")
                sampler[name] = sampling.get(s['mode'])(s['low'], s['high'], s['size'])
    elif args.train_set:
        pass
    else:
        raise AttributeError("Lack of training data, at least a sampler or a given data set is needed")


    my_net = FNN(args.layers, args.activation, args.initializer, in_d=len(sampler), out_d=len(args.output_name))
    train(sampler=sampler, output=args.output_name, constant=args.constant, icbc=args.icbc, pde=args.pde, net=my_net,
          iterations=args.max_iteration, optimizer=args.optimizer, lr=args.lr, loss_function=args.loss_function,
          path=args.save_path, report_interval=args.report_interval)

    print(time.time() - start)

if __name__ == "__main__":
    main()
