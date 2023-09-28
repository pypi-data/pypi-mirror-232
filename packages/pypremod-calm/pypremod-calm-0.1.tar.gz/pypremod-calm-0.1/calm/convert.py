import numpy as np

from calm.atomdata import molar_masses

def wt2at(symbols, weight_fractions, balance=0):
    """Converts weight fractions to atom fractions.

    Examples
    --------

    >>> wt2at(['Al', 'Si', 'Mg', 'Fe'], [0.0, 0.0043, 0.0048, 0.0020]) # AA6060
    array([  9.89567130e-01,   4.13376624e-03,   5.33218526e-03,
             9.66918268e-04])
    """
    if len(symbols) != len(weight_fractions):
        raise TypeError(
            '`symbols` and `weight_fractions` must have same length')
    #balance = _check_balance(symbols, balance)
    M = np.array([molar_masses[s] for s in symbols])
    w = np.array(weight_fractions)
    w[balance] = 1.0 - (w.sum() - w[balance])   # normalise
    return (w / M) / np.sum(w / M)


def at2wt(symbols, atom_fractions, balance=0):
    """Converts atom fractions to weight fractions.

    Examples
    --------
    >>> at2wt(['Al', 'Si', 'Mg', 'Fe'], [0.0, 0.0043, 0.0048, 0.0020]) # AA6060
    array([ 0.98708433,  0.00446772,  0.00431591,  0.00413204])
    """
    if len(symbols) != len(atom_fractions):
        raise TypeError('`symbols` and `atom_fractions` must have same length')
    #balance = _check_balance(symbols, balance)
    M = np.array([molar_masses[s] for s in symbols])
    x = np.array(atom_fractions)
    x[balance] = 1.0 - (x.sum() - x[balance])   # normalise
    return (x * M) / np.sum(x * M)

