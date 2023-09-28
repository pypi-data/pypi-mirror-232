#!/usr/bin/env python
# -*- coding:UTF-8 -*-

"""
@author: fukejie
@file: 1234567.py
@time: 2023/3/13 10:46
@desc: 
"""
""" Runs the Python version of qlknn-jetexp """


import json
import re
from pathlib import Path
from warnings import warn

import numpy as np
import pandas as pd


def test_input():
    data = {
        "Ane": 2.0,
        "x": 0.55,
        "Ate": 5.5,
        "gammaE": -0.2,
        "q": 1.8,
        "Machtor": 0.3,
        "Autor": 1.5,
        "alpha": 0.3,
        "Zeff": 1.7,
        "smag": 0.8,
        "Ani1": 2.0,
        "normni1": 0.017,
        "Ati0": 5.5,
        "Ti_Te0": 1.0,
        "logNustar": -0.9,
    }
    return data

### Classes

class QuaLiKizNDNN:
    def __init__(
        self, nn_dict, GB_scale_length=1
    ):
        """General ND fully-connected multilayer perceptron neural nn

        Initialize this class using a nn_dict. This dict is usually read
        directly from JSON, and has a specific structure. Generate this JSON
        file using the supplied function in QuaLiKiz-Tensorflow
        """
        parsed = {}
        self.GB_scale_length = GB_scale_length

        # Read and parse the json. E.g. put arrays in arrays and the rest in a dict
        for name, value in nn_dict.items():
            if name == "hidden_activation" or name == "output_activation":
                parsed[name] = value
            elif value.__class__ == list:
                parsed[name] = np.array(value)
            else:
                parsed[name] = dict(value)
        # These variables do not depend on the amount of layers in the NN
        for set in ["feature", "target"]:
            setattr(self, "_" + set + "_names", pd.Series(parsed.pop(set + "_names")))
        for set in ["feature", "target"]:
            for subset in ["min", "max"]:
                setattr(
                    self,
                    "_".join(["", set, subset]),
                    pd.Series(parsed.pop("_".join([set, subset])))[
                        getattr(self, "_" + set + "_names")
                    ],
                )
        for subset in ["bias", "factor"]:
            setattr(
                self,
                "_".join(["_feature_prescale", subset]),
                pd.Series(parsed["prescale_" + subset])[self._feature_names],
            )
            setattr(
                self,
                "_".join(["_target_prescale", subset]),
                pd.Series(parsed.pop("prescale_" + subset))[self._target_names],
            )
        self.layers = []
        # Now find out the amount of layers in our NN, and save the weigths and biases
        output_activation = parsed["output_activation"]
        if not isinstance(output_activation, list):
            output_activation = [output_activation]
        activations = parsed["hidden_activation"] + output_activation
        for ii in range(1, len(activations) + 1):
            try:
                name = "layer" + str(ii)
                weight = parsed.pop(name + "/weights/Variable:0")
                bias = parsed.pop(name + "/biases/Variable:0")
                activation = activations.pop(0)
                if activation == "tanh":
                    act = np.tanh
                elif activation == "relu":
                    act = lambda x: x * (x > 0)
                elif activation == "softplus":
                    act = lambda x: np.log(1 + np.exp(x))
                elif activation == "none":
                    act = lambda x: x
                self.layers.append(QuaLiKizNDNN.NNLayer(weight, bias, act))
            except KeyError:
                # This name does not exist in the JSON,
                # so our previously read layer was the output layer
                break
        if len(activations) == 0:
            del parsed["hidden_activation"]
            del parsed["output_activation"]
        try:
            self._clip_bounds = parsed["_metadata"]["clip_bounds"]
        except KeyError:
            self._clip_bounds = False

        # Ignore metadata
        try:
            self._metadata = parsed.pop("_metadata")
        except KeyError:
            pass
        # Ignore parsed settings
        try:
            self._parsed_settings = parsed.pop("_parsed_settings")
        except KeyError:
            pass
        if any(parsed):
            warn("nn_dict not fully parsed! " + str(parsed))

    def apply_layers(self, input, output=None):
        """Apply all NN layers to the given input

        The given input has to be array-like, but can be of size 1
        """
        input = np.ascontiguousarray(input)
        # 3x30 nn:
        # 14.1 µs ± 913 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
        # 20.9 µs ± 2.43 µs per loop (mean ± std. dev. of 7 runs, 100000 loops each)
        # 19.1 µs ± 240 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
        # 2.67 µs ± 29.7 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)

        for layer in self.layers:
            output = np.empty([input.shape[0], layer._weights.shape[1]])
            output = layer.apply(input, output)
            input = output
        return input

    class NNLayer:
        """A single (hidden) NN layer
        A hidden NN layer just does

        output = activation(weight * input + bias)

        Where weight is generally a matrix; output, input and bias a vector
        and activation a (sigmoid) function.
        """

        def __init__(self, weight, bias, activation):
            self._weights = weight
            self._biases = bias
            self._activation = activation

        def apply(self, input, output=None):
            preactivation = np.dot(input, self._weights) + self._biases
            result = self._activation(preactivation)
            return result

        def shape(self):
            return self.weight.shape

        def __str__(self):
            return "NNLayer shape " + str(self.shape())

    def get_output(
        self,
        input,
        clip_low=None,
        clip_high=None,
        output_pandas=True,
        **kwargs
    ):
        """Calculate the output given a specific input

        This function accepts inputs in the form of a dict with
        as keys the name of the specific input variable (usually
        at least the feature_names) and as values 1xN same-length
        arrays.
        """
        if isinstance(input, pd.DataFrame):
            nn_input = input[self._feature_names]
        elif isinstance(input, np.ndarray):
            nn_input = input
        else:
            raise TypeError("Invalid input passed to NN!")

        # nn_input = self._feature_prescale_factors.values[np.newaxis, :] * nn_input + self._feature_prescale_biases.values
        # 14.3 µs ± 1.08 µs per loop (mean ± std. dev. of 7 runs, 100000 loops each)
        nn_input = np.atleast_2d(self._feature_prescale_factor.values) * nn_input + np.atleast_2d(self._feature_prescale_bias.values)

        # Apply all NN layers an re-scale the outputs
        # 104 µs ± 19.7 µs per loop (mean ± std. dev. of 7 runs, 10000 loops each)
        # 70.9 µs ± 384 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each) (only apply layers)
        output = (
            self.apply_layers(nn_input) - np.atleast_2d(self._target_prescale_bias)
        ) / np.atleast_2d(self._target_prescale_factor)
        # for name in self._target_names:
        #    nn_output = (np.squeeze(self.apply_layers(nn_input)) - self._target_prescale_biases[name]) / self._target_prescale_factors[name]
        #    output[name] = nn_output
        scale_mask = [
            not any(prefix in name for prefix in ["df", "chie", "xaxis"])
            for name in self._target_names
        ]
        if self.GB_scale_length != 1 and any(scale_mask):
            output[:, scale_mask] /= self.GB_scale_length

        if isinstance(clip_low, (int, float)):
            output = np.clip(output, clip_low, None)
        if isinstance(clip_high, (int, float)):
            output = np.clip(output, None, clip_high)

        # 118 µs ± 3.83 µs per loop (mean ± std. dev. of 7 runs, 10000 loops each)
        if output_pandas:
            output = pd.DataFrame(output, columns=self._target_names)
        return output

    @classmethod
    def from_json(cls, json_file, **kwargs):
        with open(json_file) as file_:
            dict_ = json.load(file_)
        nn = cls(dict_, **kwargs)
        return nn

    @property
    def l2_norm(self):
        l2_norm = 0
        for layer in self.layers:
            l2_norm += np.sum(np.square(layer.weight))
        l2_norm /= 2
        return l2_norm

    @property
    def l1_norm(self):
        l1_norm = 0
        for layer in self.layers:
            l1_norm += np.sum(np.abs(layer.weight))
        return l1_norm

class QuaLiKizCommitteeNN(QuaLiKizNDNN):
    """
    Output wrapper which groups a set of QuaLiKizNDNN objects together,
    allowing for easy computation of prediction mean and variance.

    :arg nns: list. Set of QuaLiKizNDNN objects to group.
    """

    def __init__(
        self, nns
    ):
        self._nns = list(nns) if isinstance(nns, (list, tuple, np.ndarray)) else None

    def get_output(
        self,
        input,
        clip_low=None,
        clip_high=None,
        output_pandas=True,
        **kwargs
    ):
        output_eb = kwargs.pop("output_eb") if "output_eb" in kwargs else True
        outlist = [
            np.atleast_2d(
                nn.get_output(
                    input,
                    output_pandas=False,
                    **kwargs
                )
            )
            for nn in self._nns
        ]
        outputs = np.dstack(outlist)
        output = np.average(outputs, axis=2)
        if isinstance(clip_low, (int, float)):
            output = np.clip(output, clip_low, None)
        if isinstance(clip_high, (int, float)):
            output = np.clip(output, None, clip_high)
        # Clipping will affect error bars in clipped regions
        if output_eb:
            errorbar = np.std(outputs, axis=2)
            output = np.hstack([output, errorbar])
        if output_pandas:
            names = self._target_names if output_eb else self._base_target_names
            output = pd.DataFrame(output, columns=names)
        return output

    @property
    def _feature_names(self):
        return self._nns[0]._feature_names if len(self._nns) > 0 else None

    @property
    def _target_names(self):
        names = None
        if len(self._nns) > 0:
            names = self._nns[0]._target_names
            eb_names = pd.Series([name + "_EB" for name in self._nns[0]._target_names])
            names = names.append(eb_names)
            names = names.reset_index(drop=True)
        return names

    @property
    def _base_target_names(self):
        return self._nns[0]._target_names

class _QuaLiKizCombinedNN(QuaLiKizNDNN):
    """
    Template wrapper which combines the outputs of two QuaLiKizNDNN objects.

    :arg target_names: list. Specifies new output column names when using output_pandas option.

    :arg nns: list. QuaLiKizNDNN objects, accepts many but will only apply product to the first two.
    """

    def __init__(self, target_names, nns):
        self._nns = nns
        self._target_names = pd.Series(target_names)
        if not self._target_names.index.is_unique:
            raise Exception("Non unique index for target_names!")

    def _combo_func(self, x, y):
        pass

    def get_output(
        self,
        input,
        output_pandas=True,
        **kwargs
    ):
        pass

    @property
    def _feature_names(self):
        return self._nns[0]._feature_names

class QuaLiKizProductNN(_QuaLiKizCombinedNN):
    """
    Output wrapper which multiplies outputs of two QuaLiKizNDNN objects.

    :arg target_names: list. Specifies new output column names when using output_pandas option.

    :arg nns: list. QuaLiKizNDNN objects, accepts many but will only apply product to the first two.
    """

    def __init__(self, target_names, nns):
        if len(nns) != 2:
            raise TypeError(
                "QuaLiKizProductNN class only accepts two members!"
            )
        super().__init__(target_names, nns[:2])

    def _combo_func(self, x, y):
        return x * y

    def _error_combo_func(self, vxidx, vyidx, exidx, eyidx, x, y):
        ycomp = (
            np.power(x[:, vxidx] * y[:, eyidx], 2.0)
            if len(eyidx) > 0
            else np.zeros(x[:, vxidx].shape)
        )
        xcomp = (
            np.power(x[:, exidx] * y[:, vyidx], 2.0)
            if len(exidx) > 0
            else np.zeros(y[:, vyidx].shape)
        )
        return np.sqrt(ycomp + xcomp)

    def get_output(
        self,
        input,
        output_pandas=True,
        clip_low=None,
        clip_high=None,
        clip_x=False,
        clip_y=False,
        **kwargs
    ):
        out_indices = [
            idx for idx, name in enumerate(self._target_names) if not name.endswith("_EB")
        ]
        err_indices = [
            idx for idx, name in enumerate(self._target_names) if name.endswith("_EB")
        ]

        raw_outputs = []
        xcl = clip_low if clip_x else None
        xch = clip_high if clip_x else None
        ycl = clip_low if clip_y else None
        ych = clip_high if clip_y else None
        raw_outputs.append(
            self._nns[0].get_output(
                input,
                output_pandas=False,
                clip_low=xcl,
                clip_high=xch,
                **kwargs
            )
        )
        raw_outputs.append(
            self._nns[1].get_output(
                input,
                output_pandas=False,
                clip_low=ycl,
                clip_high=ych,
                **kwargs
            )
        )

        prod0_targets = [
            name for name in self._nns[0]._target_names if not name.endswith("_EB")
        ]
        prod0_indices = []
        for item in prod0_targets:
            prod0_indices.append(
                pd.Index(self._nns[0]._target_names.values).get_loc(item)
            )
        prod1_targets = [
            name for name in self._nns[1]._target_names if not name.endswith("_EB")
        ]
        prod1_indices = []
        for item in prod1_targets:
            prod1_indices.append(
                pd.Index(self._nns[1]._target_names.values).get_loc(item)
            )

        err0_targets = [
            name for name in self._nns[0]._target_names if name.endswith("_EB")
        ]
        err0_indices = []
        for item in err0_targets:
            err0_indices.append(
                pd.Index(self._nns[0]._target_names.values).get_loc(item)
            )
        err1_targets = [
            name for name in self._nns[1]._target_names if name.endswith("_EB")
        ]
        err1_indices = []
        for item in err1_targets:
            err1_indices.append(
                pd.Index(self._nns[1]._target_names.values).get_loc(item)
            )

        outputs = []
        if raw_outputs[0].shape == raw_outputs[1].shape:
            outputs = raw_outputs
        else:
            fullidx = 0 if raw_outputs[0].shape[1] >= raw_outputs[1].shape[1] else 1
            outputs = [
                np.zeros(raw_outputs[fullidx].shape),
                np.zeros(raw_outputs[fullidx].shape),
            ]
            outputs[fullidx] = raw_outputs[fullidx]
            if fullidx == 0:
                outputs[1][:, : raw_outputs[1].shape[1]] = raw_outputs[1]
            else:
                outputs[0][:, : raw_outputs[0].shape[1]] = raw_outputs[0]

        output = self._combo_func(*outputs)
        if len(err_indices) > 0:
            if len(prod0_indices) > 0 and len(prod1_indices) > 0:
                errorbars = self._error_combo_func(
                    prod0_indices, prod1_indices, err0_indices, err1_indices, *outputs
                )
                output[:, err_indices] = errorbars
            else:
                output[:, err_indices] = 0.0
        else:
            output = output[:, out_indices]
        if output_pandas:
            output = pd.DataFrame(output, columns=self._target_names)
        return output


class QuaLiKizDeepEnsembleNN(QuaLiKizNDNN):
    """
    """
    def __init__(self, nn_dict, mu_output_index=None, sigma_output_index=None, GB_scale_length=1):
        super().__init__(nn_dict, GB_scale_length=GB_scale_length)
        self.mu_index = mu_output_index if isinstance(mu_output_index, int) else 0
        self.sigma_index = sigma_output_index if isinstance(sigma_output_index, int) else 1
        self._base_target_names = self._target_names
        self._base_target_prescale_bias = self._target_prescale_bias
        self._base_target_prescale_factor = self._target_prescale_factor
        eb_names = pd.Series([name + "_EB" for name in self._target_names])
        self._target_names = self._base_target_names.append(eb_names).reset_index(drop=True)
        eb_biases = pd.Series([0.0 * bias for bias in self._base_target_prescale_bias])
        self._target_prescale_bias = self._base_target_prescale_bias.append(eb_biases).reset_index(drop=True)
        eb_factors = pd.Series([0.0 * factor + 1.0 for factor in self._base_target_prescale_factor])
        self._target_prescale_factor = self._base_target_prescale_factor.append(eb_factors).reset_index(drop=True)

    def apply_layers(self, input, output=None):
        """Apply all NN layers to the given input

        The given input has to be array-like, but can be of size 1
        """
        input = np.ascontiguousarray(input)
        # 3x30 nn:
        # 14.1 µs ± 913 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
        # 20.9 µs ± 2.43 µs per loop (mean ± std. dev. of 7 runs, 100000 loops each)
        # 19.1 µs ± 240 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
        # 2.67 µs ± 29.7 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)

        output_layers = self.layers[-2:]
        for layer in self.layers[:-2]:
            output = np.empty([input.shape[0], layer._weights.shape[1]])
            output = layer.apply(input, output)
            input = output
        temp = None
        if len(output_layers) > self.mu_index:
            layer = output_layers[self.mu_index]
            output = np.empty([input.shape[0], layer._weights.shape[1]])
            output = layer.apply(input, output)
            temp = output.copy()
        else:
            raise IndexError("QuaLiKizDeepEnsembleNN mu index outside of output layer length")
        if len(output_layers) > self.sigma_index:
            layer = output_layers[self.sigma_index]
            output = np.empty([input.shape[0], layer._weights.shape[1]])
            output = layer.apply(input, output)
            temp = np.hstack((temp, output))
        else:
            raise IndexError("QuaLiKizDeepEnsembleNN sigma index outside of output layer length")
        input = temp
        return input


class QuaLiKizNDNNCollection(QuaLiKizNDNN):
    """
    Wrapper for sets of QuaLiKizNDNN objects whose outputs have
    unique names. Primarily for user convenience as it condenses
    the large number of NNs into a single object.

    Currently does not provide easy functions for adding or removing
    NNs to the collection due to uniqueness of target names criteria.

    :arg nns: list. Set of NNs with unique output names to place into collection.
    """

    def __init__(self, nns):
        self._nns = nns
        if not self._feature_names.index.is_unique:
            raise Exception("Non unique index for feature_names!")

    def get_output(
        self,
        input,
        output_pandas=True,
        **kwargs
    ):
        outlist = [
            nn.get_output(
                input,
                output_pandas=output_pandas,
                **kwargs
            )
            for nn in self._nns
        ]
        output = None
        if output_pandas:
            output = outlist[0]
            for nn_out in outlist[1:]:
                output = output.join(nn_out)
        else:
            output = np.hstack(outlist)
        return output

    @property
    def _feature_names(self):
        feature_names = pd.Series()
        for nn in self._nns:
            feature_names = feature_names.append(nn._feature_names)
        feature_names = pd.Series(feature_names.unique())
        return feature_names

    @property
    def _target_names(self):
        target_names = pd.Series()
        for nn in self._nns:
            target_names = target_names.append(nn._target_names)
        target_names = pd.Series(target_names.unique())
        return target_names

###################################################################################

def generate_qlknn(nnpath):
    nn = None
    npath = Path(nnpath) if isinstance(nnpath, (str, Path)) else Path(".")
    if npath.is_dir():
        pure_nn_bases = []
        pure_nn_types = []
        impure_nn_bases = []
        impure_nn_types = []
        for nn_path in npath.glob("*.json"):
            mm1 = re.match(r"^(.+)_([^_]+).json$", str(nn_path.name))
            if mm1:
                if mm1.group(1) not in pure_nn_bases + impure_nn_bases:
                    if mm1.group(2).endswith("1"):
                        if re.search("_div_", mm1.group(1)):
                            impure_nn_bases.append(mm1.group(1))
                            impure_nn_types.append("CommitteeNN")
                        else:
                            pure_nn_bases.append(mm1.group(1))
                            pure_nn_types.append("CommitteeNN")
                    elif mm1.group(2).startswith("ens"):
                        if re.search("_div_", mm1.group(1)):
                            impure_nn_bases.append(mm1.group(1))
                            impure_nn_types.append("DeepEnsembleNN")
                        else:
                            pure_nn_bases.append(mm1.group(1))
                            pure_nn_types.append("DeepEnsembleNN")
            elif nn_path.stem not in pure_nn_bases + impure_nn_bases:
                if re.search("_div_", nn_path.stem):
                    impure_nn_bases.append(nn_path.stem)
                    impure_nn_types.append("FFNN")
                else:
                    pure_nn_bases.append(nn_path.stem)
                    pure_nn_types.append("FFNN")
            else:
                warn(str(nn_path.name) + "is not sortable")
        nns = {}
        for nn_base, nn_type in zip(pure_nn_bases, pure_nn_types):
            if nn_type == "FFNN":
                nn_obj = QuaLiKizNDNN.from_json(nn_base + ".json")
                nns[nn_obj._target_names[0]] = nn_obj
            elif nn_type == "CommitteeNN":
                nn_list = [
                    QuaLiKizNDNN.from_json(str(nn_path.resolve()))
                    for nn_path in npath.glob(nn_base + "*.json")
                ]
                nn_comm = QuaLiKizCommitteeNN(nn_list)
                nns[nn_comm._target_names[0]] = nn_comm
            elif nn_type == "DeepEnsembleNN":
                nn_ens = QuaLiKizDeepEnsembleNN.from_json(nn_base + "_ens.json")
                nns[nn_ens._target_names[0]] = nn_ens
            else:
                print("Strangeness in loading %s..." % (nn_base))
        for nn_base, nn_types in zip(impure_nn_bases, impure_nn_types):
            if nn_type == "FFNN":
                nn_obj = QuaLiKizNDNN.from_json(nn_base + ".json")
                mmm = re.match(r"^(.+)_div_(.+)$", nn_obj._target_names[0])
                if mmm and mmm.group(2) in nns:
                    nn_obj = QuaLiKizProductNN(
                        [mmm.group(1)], [nn_obj, nns[mmm.group(2)]]
                    )
                nns[nn_obj._target_names[0]] = nn_obj
            elif nn_type == "CommitteeNN":
                nn_list = [
                    QuaLiKizNDNN.from_json(str(nn_path.resolve()))
                    for nn_path in npath.glob(nn_base + "*.json")
                ]
                nn_comm = QuaLiKizCommitteeNN(nn_list)
                mmm = re.match(r"^(.+)_div_(.+)$", nn_comm._target_names[0])
                if mmm and mmm.group(2) in nns:
                    nn_comm = QuaLiKizProductNN(
                        [mmm.group(1), mmm.group(1) + "_EB"], [nn_comm, nns[mmm.group(2)]]
                    )
                nns[nn_comm._target_names[0]] = nn_comm
            elif nn_type == "DeepEnsembleNN":
                nn_ens = QuaLiKizDeepEnsembleNN.from_json(nn_base + "_ens.json")
                mmm = re.match(r"^(.+)_div_(.+)$", nn_ens._target_names[0])
                if mmm and mmm.group(2) in nns:
                    nn_ens = QuaLiKizProductNN(
                        [mmm.group(1), mmm.group(1) + "_EB"], [nn_ens, nns[mmm.group(2)]]
                    )
                nns[nn_ens._target_names[0]] = nn_ens
            else:
                print("Strangeness in loading %s..." % (nn_base))
        nn = QuaLiKizNDNNCollection(list(nns.values()))
    return nn

def evaluate_qlknn(inp, nnpath):
    outp = None
    nn = generate_qlknn(nnpath)
    extra_options = {"clip_low": 0.0, "clip_y": True}
    outp = nn.get_output(inp, output_pandas=True, **extra_options)
    return outp

def main():
    scann = 11
    data = test_input()
    data["Ati0"] = np.linspace(-2.0, 18, scann)
    inp = pd.DataFrame(data)
    outp = evaluate_qlknn(inp, ".")
    print(outp)

if __name__ == "__main__":
    main()
