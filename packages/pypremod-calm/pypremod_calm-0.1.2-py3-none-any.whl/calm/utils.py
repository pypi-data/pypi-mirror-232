"""General utilities."""
import numpy as np

from calm.constants import atomic_numbers, molar_masses


def convert_X2C(elements, X):
    """Returns `X` converted from atom-fractions to weight percent."""
    M = np.array([molar_masses[atomic_numbers[e]] for e in elements])
    if np.ndim(X) == 1:
        XM = X * M
        C = 100. * XM / XM.sum()
    else:
        XM = X * M[None, :]
        C = 100. * np.array(XM / XM.sum(axis=-1)[:, None])
    C[np.isnan(C)] = 0.0
    return C


def convert_C2X(elements, C):
    """Returns `C` converted from weight percent to atom-fractions."""
    M = np.array([molar_masses[atomic_numbers[e]] for e in elements])
    if np.ndim(C) == 1:
        y = C / M
        X = y / y.sum()
    else:
        y = C / M[None, :]
        X = np.array(y / y.sum(axis=-1)[:, None])
    X[np.isnan(X)] = 0.0
    return X
