# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function

import warnings

import numpy as np


class CBArrayError(Exception):
    pass


class cbarray(np.ndarray):
    """Subclass of numpy.ndarray that allows registering callbacks for
    handeling modified elements."""
    def __new__(cls, *args, **kw):
        cb = kw.pop('cb', 'raise')
        obj = super(cbarray, cls).__new__(cls, *args, **kw)
        obj._setitem_cb = cb
        return obj

    def __setitem__(self, i, value):
        if self._setitem_cb == 'raise':
            raise CBArrayError(
                'Attempting to set element %r of a fix array' % (i, ))
        elif self._setitem_cb:
            self._setitem_cb(self, i, value)
        else:
            super(cbarray, self).__setitem__(i, value)


def array(obj, dtype=None, copy=False, order='K', subok=False, ndmin=0,
          cb='raise'):
    """Creates a cbarray.  Corresponds to np.array()."""
    a = np.array(obj, dtype=dtype, copy=copy, order=order, subok=subok,
                 ndmin=ndmin)
    order = 'F' if np.isfortran(a) else 'C'
    return cbarray(shape=a.shape, dtype=a.dtype, buffer=a, strides=a.strides,
                   order=order, cb=cb)


def zeros(shape, dtype=float, order='C', cb='raise'):
    """Returns a new cbarray of given shape and type, filled with zeros."""
    arr = cbarray(shape=shape, dtype=dtype, order=order, cb=cb)
    arr.flat[:] = 0
    return arr


def ones(shape, dtype=float, order='C', cb='raise'):
    """Returns a new cbarray of given shape and type, filled with ones."""
    arr = cbarray(shape=shape, dtype=dtype, order=order, cb=cb)
    arr.flat[:] = 1
    return arr
