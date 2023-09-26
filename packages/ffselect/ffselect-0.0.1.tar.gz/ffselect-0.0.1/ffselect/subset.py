from collections.abc import Callable
from typing import Any
import sys


def MinSubsetSelection(data: Any, target: str, fit_function: Callable[[Any, list[str], str], float], features: list[str]
                       , loss: bool = True, interactive: bool = True) -> tuple[float, list[str]]:
    """
    Minimal feature subset selection algorithm in n*log(n)
    :param data: Input data to pass to the fitting function
    :param target: Target parameter feature name
    :param fit_function: Callable function that fits the model and returns R^2/loss
    :param features: List of feature names
    :param loss: Set to true (by default) if the fitting function returns loss, R^2 otherwise
    :param interactive: Print output (default True)
    :return: Tuple with the resulting R^2/loss and the list of features
    """
    train_features = features

    if target in train_features:
        train_features.remove(target)

    # In this function param is either loss or R^2
    param = 0
    if loss:
        param = sys.maxsize

    res_features = []
    n = len(train_features)

    # Param with all features enabled
    initial_param = 0

    if interactive:
        if loss:
            f_string = "[{}/{}]: feature: {}, loss: {:.6f} -> {:.6f} ({:.6f})"
        else:
            f_string = "[{}/{}]: feature: {}, R^2: {:.6f} -> {:.6f} ({:.6f})"

    for i in range(n - 1):
        param_local = 0
        if loss:
            param_local = sys.maxsize

        min_f = []

        # used only for output
        feature_drop = ""

        for j in range(-1, len(train_features)):
            if j == -1:
                # Initial pass with all features
                f = train_features
                drop = ""
            else:
                if j < len(train_features) - 1:
                    f = train_features[:j] + train_features[j + 1:]
                else:
                    f = train_features[:j]
                drop = train_features[j]

            # execute the callable
            p = fit_function(data, f, target)

            if i == 0 and j == -1:
                # All features enabled
                initial_param = p

            if loss:
                if p < param_local:
                    param_local = p
                    min_f = f
                    feature_drop = drop
            else:
                if p > param_local:
                    param_local = p
                    min_f = f
                    feature_drop = drop

        if min_f == train_features:
            # We cannot optimize further
            res_features = min_f
            param = param_local
            break

        if interactive:
            if i == 0:
                if loss:
                    print(f_string.format(i + 1, n, feature_drop, initial_param, param_local,
                                          param_local - initial_param))
                else:
                    print(f_string.format(i + 1, n, feature_drop, initial_param, param_local,
                                          initial_param - param_local))
            else:
                if loss:
                    print(f_string.format(i + 1, n, feature_drop, param, param_local, param_local - param))
                else:
                    print(f_string.format(i + 1, n, feature_drop, param, param_local, param - param_local))

        res_features = min_f
        train_features = min_f
        param = param_local

    return param, res_features


def FastSubsetSelection(data: Any, target: str, fit_function: Callable[[Any, list[str], str], float], features: list[str]
                       , threshold: float = None, loss: bool = True, interactive: bool = True) -> tuple[float, list[str]]:
    """
    Fast feature subset selection algorithm in linear time. May drop important features
    :param data: Input data to pass to the fitting function
    :param target: Target parameter feature name
    :param fit_function: Callable function that fits the model and returns R^2/loss
    :param features: List of feature names
    :param threshold: Minimal difference in loss/R^2 at which we drop the feature
    :param loss: Set to true (by default) if the fitting function returns loss, R^2 otherwise
    :param interactive: Print output (default True)
    :return: Tuple with the resulting R^2/loss and the list of features
    """
    train_features = features

    if target in train_features:
        train_features.remove(target)

    param = 0
    if loss:
        param = sys.maxsize

    if interactive:
        if loss:
            f_string = "[{}/{}]: feature: {}, loss: {:.6f} -> {:.6f} ({:.6f})"
        else:
            f_string = "[{}/{}]: feature: {}, R^2: {:.6f} -> {:.6f} ({:.6f})"

    for i in range(len(features), -1, -1):
        drop = ""

        if i < len(train_features) - 1:
            f = train_features[:i] + train_features[i + 1:]
            drop = train_features[i]
        elif i == len(train_features) - 1:
            f = train_features[:i]
            drop = train_features[i]
        else:
            # Initial pass with all features
            f = train_features

        # Execute the callable
        p = fit_function(data, f, target)

        updated = False
        last_param = param
        if loss:
            if p < param and (threshold is None or param - p >= threshold):
                param = p
                train_features = f
                updated = True
        else:
            if p > param and (threshold is None or p - param >= threshold):
                param = p
                train_features = f
                updated = True

        if not interactive or not updated or i == len(features):
            continue

        if loss:
            print(f_string.format(len(features) - i, len(features), drop, last_param, param, param - last_param))
        else:
            print(f_string.format(len(features) - i, len(features), drop, last_param, param, last_param - param))

    return param, train_features
