# -*- coding: utf-8 -*-
"""
General material parameters.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from calm import get_entity

BaseMicrostructure = get_entity('Microstructure', '0.1',
                                namespace='http://www.sintef.no/calm')


class Microstructure(BaseMicrostructure):
    """Class describing some general aspects of a microstructure.

    Initial values for the attributes may be provided as keyword arguments.

    Parameters
    ----------
    uuid : string
        UUID of SOFT instance to initialise values from. Requires softpy.
    driver : None | "json" | "hdf5" | "mongo" | ...
        The driver to use for loading initial values.  Requires softpy.
    uri : string
        URI to initial values.  Requires softpy.
    options : None | string
        Additional options passed to the driver.
    **kwags :
        Initial values for attributes.

    Attributes
    ----------
    grainsize : float
         Average grain size, m
    delta : float
         Average subgrain size, m
    rho_i : float
         Interior dislocation density, m^-2
    X : float
         Fraction recrystallised
    theta : float
         Average misorientation between low-angle grain boundaries, degree
    phi : float
         Average misorientation between high-angle grain boundaries, degree
    """
    def __init__(self, uuid=None, driver=None, uri=None, options=None,
                 **kwargs):
        super(Microstructure, self).__init__(uuid=uuid, driver=driver,
                                             options=options, **kwargs)

        for k in kwargs.keys():
            if k not in self._property_names:
                raise NameError(
                     'Microstructure has no such keyword argument: %s' % k)
