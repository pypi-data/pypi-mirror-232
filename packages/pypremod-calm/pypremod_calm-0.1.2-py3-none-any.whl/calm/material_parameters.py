# -*- coding: utf-8 -*-
"""
General material parameters.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np

import calm
from calm import get_entity, HAVE_SOFTPY


BaseMaterialParameters = get_entity('MaterialParameters', '0.1',
                                    namespace='http://www.sintef.no/calm')


# Default diffusivities, assuming aluminium alloys
# Simple binary diffusion coefficients taken from the literature.
diffusivities = {
    # ele  D0(m^2/s) Q(J/mol)    Reference, DOI
    'Al': (1.76e-5,  126e3),   # https://doi.org/10.1002/pssa.19700010333
    'Ti': (1.12e-1,  260e3),   # doi:10.1016/S0921-5093(03)00624-5
    'V':  (1.60,     302.5e3), # doi:10.1016/S0921-5093(03)00624-5
    'Cr': (6.75e-1,  261.9e3), # doi:10.1016/S0921-5093(03)00624-5
    'Mn': (1.35e-2,  211.5e3), # doi:10.1016/S0921-5093(03)00624-5
    'Fe': (3.62e-1,  214.0e3), # doi:10.1016/S0921-5093(03)00624-5
    'Co': (1.93e-2,  168.4e3), # doi:10.1016/S0921-5093(03)00624-5
    'Ni': (4.10e-4,  144.6e3), # doi:10.1016/S0921-5093(03)00624-5
    'Cu': (4.44e-5,  133.9e3), # doi:10.1016/S0921-5093(03)00624-5
    'Zn': (1.19e-5,  116.1e3), # doi:10.1016/S0921-5093(03)00624-5
    'Mg': (1.49e-5,  120.5e3), # doi:10.1016/S0921-5093(03)00624-5
    'Si': (1.38e-5,  117.6e3), # doi:10.1016/S0921-5093(03)00624-5
    'Ga': (4.90e-5,  122.4e3), # doi:10.1016/S0921-5093(03)00624-5
    'Ge': (4.80e-5,  121.3e3), # doi:10.1016/S0921-5093(03)00624-5
    #
    #'Si': (8.3e-7,   78.1e3), # https://doi.org/10.1016/0040-6090(85)90073-2
    #'Zn': (2.0e-5,   121e3),  # https://doi.org/10.1080/13642817808246394
    #'Co': (1.41e-2,  169e3),  # https://doi.org/10.1080/13642817808246394
    #'Ni': (4.4e-4,   146e3),  # https://doi.org/10.1080/13642817808246394
    #'Cu': (1.50e-5,  30.2e3), # https://doi.org/10.1063/1.1713963
    #'Zn': (3.14e-5,  76.6e3), # https://www.nist.gov/sites/default/files/documents/mml/msed/thermodynamics_kinetics/Final-version-NIST-2010-diffusion-workshop-March-24-2010-Yong-Du-China.pdf
    #'Mg': (0, 0),  # https://doi.org/10.1016/0378-5963(81)90023-4
    #           # https://doi.org/10.1016/0036-9748(70)90182-1
    #      https://www.jstage.jst.go.jp/article/matertrans/43/2/43_2_232/_pdf
    #           # https://doi.org/10.1016/j.calphad.2015.03.002
    # 'Mn':     # https://doi.org/10.4028/www.scientific.net/MSF.13-14.539
}


class MaterialParameters(BaseMaterialParameters):
    """Class providing some general material parameters.  Default values
    are typical for aluminium.

    Parameters
    ----------
    elements : sequence of strings
        Chemical symbol of each element.  Either `elements` or `uuid`
        must be provided.
    uuid : string
        UUID of SOFT instance to initialise values from. Requires softpy.
    driver : None | "json" | "hdf5" | "mongo" | ...
        The driver to use for loading initial values.  Requires softpy.
    uri : string
        URI to initial values.  Requires softpy.
    options : None | string
        Additional options passed to the driver.
    kwargs :
        Additional keyword arguments passed to SOFT initialiser.

    Note
    ----
    The diffusivity of element `i` is given by ``D_i = D0*exp(Q/(Rgas*T))``.
    """
    def __init__(self, elements=None, uuid=None, driver=None,
                 uri=None, options=None, **kwargs):
        # Defaults, overwritten by keyword arguments
        self.b = 2.86e-10    # Length of Burger's vector, m
        self.MTaylor = 3.1   # Taylor factor
        self.v_D = 1.0e13    # Debye frequency, 1/s
        self.nu = 0.32       # Poisson ratio

        if HAVE_SOFTPY:
            if elements is None and uuid is None:
                raise ValueError('either `elements` or `uuid` must be provided')
            kw = kwargs.copy()
            if elements is not None:
                kw['elements'] = np.array(elements, dtype=str)
            super(MaterialParameters, self).__init__(uuid=uuid, driver=driver,
                                                     options=options, **kw)
        else:
            super(MaterialParameters, self).__init__(uuid=uuid, driver=driver,
                                                     options=options)
            if elements is None:
                raise ValueError('`elements` must be provided')
            self.elements = np.array(elements, dtype=str)
            for k, v in kwargs.items():
                if k in ('b', 'MTaylor', 'v_D', 'nu'):
                    setattr(self, k, float(v))
                elif k in ('D0', 'Q'):
                    setattr(self, k, np.array(v, dtype=float))
                else:
                    raise NameError(
                        'MaterialParameters has no such argument: %s' % k)

        if not uuid and 'D0' not in kwargs:
            self.D0 = np.array([diffusivities[e][0] for e in self.elements])
        if not uuid and 'Q' not in kwargs:
            self.Q = np.array([diffusivities[e][1] for e in self.elements])

    nelements = property(lambda self: len(self.elements),
                         doc='Number of different chemical elements')

    def diffusivities(self, T):
        """Returns the diffusivity of each element at temptrature `T` (K)."""
        return self.D0 * np.exp(-self.Q / (calm.constants.Rgas * T))
