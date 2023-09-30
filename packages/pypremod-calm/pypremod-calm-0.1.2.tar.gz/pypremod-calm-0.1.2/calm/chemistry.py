# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import warnings
import math

import numpy as np
import matplotlib.pyplot as plt

from calm import HAVE_SOFTPY, get_entity
from calm.constants import pi, NA, atomic_numbers, molar_masses, atomic_radii
from .utils import convert_C2X
from . import cbarray as ca

BaseChemistry = get_entity(
    'Chemistry', '0.1', 'http://www.sintef.no/calm')
BaseChemistrySizeDistribution = get_entity(
    'ChemistrySizeDistribution', '0.1', 'http://www.sintef.no/calm')


class NotEnoughSoluteError(ValueError):
    """Raised if there is not enough solute to add or increase the amount
    of a phase."""
    pass


class ChemistrySizeDistribution(BaseChemistrySizeDistribution):
    """Class describing the alloy composition and particle size distribution.

    Parameters
    ----------
    elements : sequence of strings
        Chemical symbol of each chemical element.  By convension the
        dependent element (e.g. Al) is listed first.
        Required if `uuid` is not given; [nelements]
    phases : sequence of strings
        Name of phases.  Matrix should be listed first.
        Required if `uuid` is not given; [nphases]
    X0 : sequence of floats
        Nominal alloy composition in atom-fractions; [nelements]
    C0 : sequence of floats
        Nominal alloy composition in weight-percent; [nelements]
    uuid : string
        UUID of SOFT instance to initialise values from. Requires softpy.
    driver : None | "json" | "hdf5" | "mongo" | ...
        The driver to use for loading initial values.  Requires softpy.
    uri : string
        URI to initial values.  Requires softpy.
    options : None | string
        Additional options passed to the driver.
    **kwargs :
        Additional keyword arguments passed to SOFT initialiser.

    Note
    ----
    Either X0 or C0 are required if `uuid` is not given.

    This class should confirm to the SOFT entity
    ChemistrySizeDistribution version 0.1.  We refer to that for a
    description of attributes.
    """
    def __init__(self, elements=None, phases=None, X0=None, C0=None,
                 uuid=None, driver=None, uri=None, options=None, **kwargs):
        super(ChemistrySizeDistribution, self).__init__(
            uuid=uuid, driver=driver, uri=uri, options=options,
            uninitialize=False, **kwargs)

        if elements is None or phases is None:
            return

        nelements = len(elements)
        nphases = len(phases)
        ndomains = 0
        for k in 'Xd', 'rd', 'shape', 'Nd', 'phasenames', 'atvol':
            if k in kwargs:
                if ndomains == 0:
                    ndomains = len(kwargs[k])
                elif ndomains != len(kwargs[k]):
                    raise TypeError('inconsistent number of domains')

        if X0 is not None:
            X0 = np.array(X0, dtype=float)
        elif C0 is not None:
            X0 = convert_C2X(elements, C0)
        else:
            X0 = np.zeros((nelements,))
        X0[0] = 1.0 - X0[1:].sum()  # enforce balance

        self.elements = np.array(elements, dtype=str)
        self.phases = np.array(phases, dtype=str)
        self.X0 = np.array(X0)

        self.Xd = np.zeros(shape=(ndomains, nelements), dtype=float)
        self.rd = np.zeros(shape=(ndomains, ), dtype=float)
        self.shape = np.ones(shape=(ndomains, ), dtype=float)
        self.Nd = np.zeros(shape=(ndomains, ), dtype=float)
        self.phasenames = np.zeros(shape=(ndomains, ), dtype='U20')
        self.atvol = np.zeros(shape=(ndomains, ), dtype=float)
        self.atvol0 = kwargs.pop('atvol0', 0.0)

        for k, v in kwargs.items():
            if k not in self._property_names:
                raise TypeError('ChemistrySizeDistribution takes no such '
                                'argument: %s' % k)
            getattr(self, k)[:] = v

        if not self.atvol.any():
            self.atvol[:] = self.estimated_atvol()

        if not self.atvol0:
            self.atvol0 = self.estimated_atvol('nominal')

    nelements = property(lambda self: len(self.elements),
                         doc='Number of different chemical elements')
    nphases = property(lambda self: len(self.phases),
                       doc='Number of phases.')
    ndomains = property(lambda self: len(self.Xd),
                        doc='Number of geometrical (size) domains.')

    def estimated_atvol(self, granularity='domain'):
        """Returns an array with estimated average volumes per atom, based on
        tabulated metallic (r_met) and covalent (r_cov) radii.

        `granularity` must be be one of:
            "domain"   - per domain (r_cov)
            "phase"    - per phase (matrix: r_met, other: r_cov)
            "nominal"  - overall (matrix: r_met, other: r_cov)
        """
        inds = [atomic_numbers[e] for e in self.elements]
        r_cov = atomic_radii.r_cov[inds] * 1e-12
        r_cov[np.isnan(r_cov)] = 0.2e-10
        r_emp = atomic_radii.r_emp[inds] * 1e-12
        r_met = atomic_radii.r_met[inds] * 1e-12
        r_met[np.isnan(r_met)] = r_emp[np.isnan(r_met)]
        r_met[np.isnan(r_met)] = r_cov[np.isnan(r_met)]
        #v_cov = 4 * pi / 3 * r_cov ** 3
        #v_met = 4 * pi / 3 * r_met ** 3
        v_cov = 4 * np.sqrt(2) * r_cov ** 3  # close-packed (?)
        v_met = 4 * np.sqrt(2) * r_met ** 3  # close-packed
        if granularity == 'domain':
            atvol = np.dot(self.Xd, v_cov)
        elif granularity == 'phase':
            atvol = np.zeros((self.nphases, ))
            atvol[0] = np.dot(self.Xp[0], v_met)
            atvol[1:] = np.dot(self.Xp[1:], v_cov)
        elif granularity == 'nominal':
            #atvol = np.sum(self.volfrac * self.estimated_atvol('phase'))
            atvol = np.dot(self.X0, v_met)
        else:
            raise ValueError('`granularity` muse be either "domain", "phase" '
                             'or "phase". Got "%s"' % (granularity, ))
        return atvol

    def get_phase_indices(self):
        """Returns an array of length `ndomains` containing the indices
        of the phase that each domain belongs to."""
        idx = {p: i for i, p in enumerate(self.phases)}
        return np.array([idx[p] for p in self.phasenames], dtype='int8')

    def get_Xp(self):
        """Returns an array of shape ``(nphase, nelements)`` with average
        composition of each phase."""
        Xp = np.zeros(shape=(self.nphases, self.nelements), dtype=float)
        x = (self.Vd * self.Nd)[:, None] * self.Xd
        for j, p in enumerate(self.phases):
            mask = self.phasenames == p
            Xp[j, :] = self.alpha[j] * np.sum(x[mask], axis=0)
        div = Xp.sum(axis=1)[:, None]
        Xp = np.divide(Xp, div, where=div > 1e-9)

        # Matrix from solute balance (it should be first phase and not among
        # any phases in phasenames
        if self.phases[0] in self.phasenames:
            warnings.warn('First phase should be matrix, but is mentioned in '
                          '`phasenames` - no solute balance is imposed')
        else:
            f = self.volfrac
            Xp[0] = (self.X0 - np.sum(f[1:, None] * Xp[1:], axis=0)) / f[0]

        #assert np.all(0.0 <= Xp) and np.all(Xp <= 1.0)
        return Xp

    def set_Xp_i(self, i, value):
        """Sets average composition of phase `i`.

        Length of `value` should equal `nelements` and sum to one (if
        not, first element is balanced).

        """
        assert i != 0, 'cannot set matrix composition'
        assert len(value) == self.nelements, '`value` length must be nelements'
        value[0] = 1.0 - sum(value[1:])
        assert min(value) >= 0 and max(value <= 1), '`value` out of range'

        Xd = self.Xd.copy()
        Xp = self.get_Xp()
        self.Xd[self.phaseindices == i] *= value / Xp[i]

        Xss = Xp[0]
        if min(Xss) < 0 or max(Xss) > 1:
            self.Xd.flat[:] = Xd
            raise ValueError(
                'set_Xd_i(%d, %r) => Xss out of range' % (i, value))

    def set_Xp(self, value):
        """sets volume fractions."""
        for i in range(1, self.nphases):
            self.set_Xp_i(i, value[i])

    def _Xp_cb(self, arr, i, value):
        self.set_Xp_i(i, value)

    def get_volfrac(self):
        """Returns an array with the volume fraction of each phase."""
        volfrac = np.zeros(shape=(self.nphases, ), dtype=float)
        f = self.Vd * self.Nd
        for i, ph in enumerate(self.phases):
            mask = self.phasenames == ph
            volfrac[i] = np.sum(f[mask])
        volfrac[0] = 1.0 - volfrac[1:].sum()
        #return ca.array(volfrac, cb=self._volfrac_cb)
        return volfrac

    def set_volfrac_i(self, i, value):
        """Sets volume fraction of phase `i` to `value`.

        This is done by scaling the number densities for all domains
        corresponding to phase `i`.
        """
        volfrac = self.get_volfrac()
        N = self.Nd.copy()
        if i == 0:
            self.Nd *= (1 - value) / (1 - volfrac[0])
        else:
            self.Nd[self.phaseindices == i] *= value / volfrac[i]

        Xp = self.get_Xp()
        if Xp.min() < 0 or Xp.max() > 1:
            self.Nd[:] = N
            raise ValueError(
                'set_volfrac_i(%d, %f) => Xp out of range' % (i, value))

    def set_volfrac(self, volfrac):
        """sets volume fractions."""
        for i in range(1, self.nphases):
            self.set_volfrac_i(i, volfrac[i])

    def _volfrac_cb(self, arr, i, value):
        self.set_volfrac_i(i, value)

    def get_partdens(self):
        """Returns the particle number density for each phase."""
        partdens = np.zeros((self.nphases, ))
        for j, p in enumerate(self.phases):
            mask = self.phasenames == p
            partdens[j] = np.sum(self.Nd[mask])
        return partdens

    def get_atvol(self, granularity='phase'):
        """Returns the average volume per atom.  `granularity` must be either
        "domain" or "phase"."""
        if granularity == 'domain':
            atvol = self.atvol
        elif granularity == 'phase':
            atvol = np.zeros(shape=(self.nphases, ))
            atN = self.atvol * self.Nd
            for j, p in enumerate(self.phases):
                mask = self.phasenames == p
                N = np.sum(self.Nd[mask])
                if N:
                    atvol[j] = np.sum(atN[mask]) / N
            # matrix from volume balance
            f = self.volfrac
            atvol[0] = (self.atvol0 - np.sum(f[1:] * atvol[1:])) / f[0]
        else:
            raise ValueError('`granularity` muse be either "domain" or "phase" '
                             'Got "%s"' % (granularity, ))
        return atvol

    def set_atvol(self, atvol, granularity='phase'):
        """Returns the average volume per atom.  `granularity` must be either
        "domain" or "phase"."""
        if granularity == 'domain':
            self.atvol[:] = atvol
        elif granularity == 'phase':
            for j, p in enumerate(self.phases):
                mask = self.phasenames == p
                self.atvol[mask] = atvol[j]
        else:
            raise ValueError('`granularity` muse be either "domain" or "phase" '
                             'Got "%s"' % (granularity, ))

    def get_alpha(self, granularity='phase'):
        """Returns ratio between nominal average atomic volume and average
        atomic volume for each domain/phase.

        The `granularity` must be either "domain" or "phase".
        """
        if granularity == 'domain':
            alpha = np.divide(self.atvol0, self.atvol, where=self.atvol > 1e-40)
        elif granularity == 'phase':
            atvol = self.get_atvol('phase')
            alpha = np.divide(self.atvol0, atvol, where=atvol > 1e-40)
            f = self.volfrac
            alpha[0] = (1.0 - np.sum(f[1:] * alpha[1:])) / f[0]
        else:
            raise ValueError('`granularity` muse be either "domain" or "phase" '
                             'Got "%s"' % (granularity, ))
        return alpha

    def to_wt(self, X):
        """Returns `X` converted from atom-fractions to wt%."""
        M = np.array([molar_masses[atomic_numbers[e]] for e in self.elements])
        if np.ndim(X) == 1:
            XM = X * M
            return 100. * XM / XM.sum()
        else:
            XM = X * M[None, :]
            C = np.array(100. * XM / XM.sum(axis=-1)[:, None])
            C[np.isnan(C)] = 0.0
            return C

    def get_cp(self):
        """Returns the composition of each phase in mol/m^3."""
        atvol = self.get_atvol('phase')[:, None]
        return np.divide(self.Xp, NA * atvol, where=atvol > 1e-40)

    def get_rmean(self):
        """Returns the mean equivalent spherical radius of each phase in m."""
        rmean = np.zeros((self.nphases, ))
        rN = self.rd * self.Nd
        tol = self.Nd.sum() * 1e-12
        for j, ph in enumerate(self.phases):
            mask = self.phasenames == ph
            sumN = np.sum(self.Nd[mask])
            if sumN > tol:
                rmean[j] = np.divide(np.sum(rN[mask]), sumN, where=sumN > tol)
            else:
                rmean[j] = 0.0
        return rmean

    def set_rmean_i(self, i, value):
        """Sets mean radius of phase `i` to `value`.

        This is done by scaling the particle radii for all domains
        corresponding to phase `i`.
        """
        rmean = self.get_rmean()
        rd = self.rd.copy()
        self.rd[self.phaseindices == i] *= value / rmean[i]

        Xp = self.get_Xp()
        if Xp.min() < 0 or Xp.max() > 1:
            self.rd[:] = rd
            raise ValueError(
                'set_rmean_i(%d, %f) => Xp out of range' % (i, value))

    def set_rmean(self, value):
        """sets mean particle radii."""
        for i in range(1, self.nphases):
            self.set_rmean_i(i, value[i])

    def _rmean_cb(self, arr, i, value):
        self.set_rmean_i(i, value)

    def get_rstd(self):
        """Returns the standard deviation of the sizes for each phase. m"""
        rstd2 = np.zeros((self.nphases, ))
        for j in range(1, self.nphases):
            mask = self.phaseindices == j
            N = self.Nd[mask]
            r = self.rd[mask]
            rmean = np.sum(r * N) / np.sum(N)
            rstd2[j] = np.sum(r ** 2 * N) / np.sum(N) - rmean ** 2
        return np.sqrt(rstd2)

    phaseindices = property(
        lambda self: ca.array(self.get_phase_indices()),
        doc='Indices of phase that each domain belongs to; [nelements]')
    Xp = property(
        lambda self: ca.array(self.get_Xp(), cb=self._Xp_cb),
        lambda self, value: self.set_Xp(value),
        doc='Average composition of each phase; [nphases, nelements], '
        'atom-fraction')
    volfrac = property(
        lambda self: ca.array(self.get_volfrac(), cb=self._volfrac_cb),
        #lambda self: self.get_volfrac(),
        lambda self, value: self.set_volfrac(value),
        doc='Volume fraction of each phase; [nphases]')
    partdens = property(
        lambda self: ca.array(self.get_partdens()),
        doc='Particle number density for each phase; [nphases], 1/m³')
    alpha = property(
        lambda self: ca.array(self.get_alpha()),
        doc='Ratio between nominal average atomic volume and average atomic '
        'volume for each phase [nphases]')
    Xss = property(
        lambda self: ca.array(self.Xp[0]),
        doc='Solid solution composition; [nelements], atom-fraction')
    Vd = property(
        lambda self: ca.array(4 * pi / 3 * self.rd ** 3),
        doc='Volume of each domain, [ndomains], m³')
    Sd = property(
        lambda self: ca.array(4 * pi / self.shape ** (2 / 3) * self.rd ** 2),
        doc='Surface area of each domain, [ndomains], m²')
    rmean = property(
        lambda self: ca.array(self.get_rmean(), cb=self._rmean_cb),
        lambda self, value: self.set_rmean(value),
        doc='Mean size of each phase; [nphases], m')
    rstd = property(
        lambda self: ca.array(self.get_rstd()),
        doc='standard deviation of sizes for each phase; [nphases], m')

    C0 = property(lambda self: ca.array(self.to_wt(self.X0)),
                  doc='Nominal composition; [nelements], wt%')
    Cp = property(lambda self: ca.array(self.to_wt(self.Xp)),
                  doc='Composition of each phase; [nphases, nelements], wt%')
    Css = property(lambda self: ca.array(self.to_wt(self.Xss)),
                  doc='Solid solution composition; [nelements], wt%')
    c0 = property(lambda self: ca.array(np.dot(self.volfrac, self.cp)),
                  doc='Nominal composition of each phase; [nphases], mol/m³')
    cp = property(lambda self: ca.array(self.get_cp()),
                  doc='Composition of each phase; [nphases, nelements], '
                  'mol/m^3')
    css = property(lambda self: ca.array(self.cp[0]),
                  doc='Solid solution composition; [nelements], mol/m³')

    def __str__(self):
        s = ['%10s  %9s  %9s  ' % ('[at%]', 'f(%)', 'rmean(nm)') +
             ' '.join('%6s' % e for e in self.elements)]
        s.append('%10s  %9s  %9s  ' % ('X0', '', '') +
                 ' '.join('%6.3f' % (100 * X) for X in self.X0))
        s.append('%10s  %9s  %9s  ' % ('C0(wt%)', '', '') +
                 ' '.join('%6.3f' % C for C in self.C0))
        s.append('%10s  %9s  %9s  ' % ('Css(wt%)', '', '') +
                 ' '.join('%6.3f' % C for C in self.Css))
        f = self.get_volfrac()
        rmean = self.get_rmean()
        Xp = self.get_Xp()
        for j, ph in enumerate(self.phases):
            s.append('%10s  %9.3f  %9.1f  ' % (ph, 100 * f[j], 1e9 * rmean[j]) +
                     ' '.join('%6.3f' % (100 * X) for X in Xp[j]))
        return '\n'.join(s)

    def add_phase(self, name, Xp, rd, Nd=None, volfrac=None,
                  distribution='lognormal', rmean=None, rstd=None, shape=1,
                  atvol=None, reduce_volfrac=False):
        """Adds a new phase.

        `n` new domains (size classes) corresponding to this phase
        will also be added.

        Parameters
        ----------
        name : string
            Name of the new phase.
        Xp : array_like, shape: (nelements, ) | (n, nelements) | dict
            Composition of the new phase in atom-fractions. May also be
            given as a dict mapping atom symbols to content.
        rd : n floats
            Center of size classes for the new phase. m
        Nd : n floats
            Number density of each size class. If None, it is derived from
            `volfrac`.  1/m³
        volfrac : float
            Volume fraction of the new phase.  Used if `Nd` is not given.
        distribution : "lognormal" | "LSW" | "gamma" | "exp"
            Size distribution.  Used if `Nd` is not given.
        rmean : float
            Mean of size distribution.  Used if `Nd` is not given. m
            `distribution`.
        rstd : float
            Standard deviation of size distribution.  Used if `Nd` is not
            given. Defaults to ``0.2 * rmean``. m
        shape : float | n floats
            Shape parameter for each size class.  If a scalar is provided,
            it is applied to all size classes.
        atvol : None | float | n floats
            Average volume per atom in the new phase.  If None, it will be
            estimated. m³
        reduce_volfrac : bool
            Whether to reduce the volume fraction in case there is not
            solute enough for the phase.  If false, a NotEnoughSoluteError
            is raised and the object is left unchanged.
        """
        if name in self.phases:
            raise KeyError('Phase %r already exists' % name)
        if volfrac is None and Nd is None:
            raise TypeError('Either `volfrac` or `Nd` must be provided')
        n = 1 if np.isscalar(rd) else len(rd)
        if hasattr(Xp, 'items'):
            Xp = [Xp.get(s, 0.0) for s in self.elements]
        Xp = np.ones((n, 1)) * Xp
        rd = np.ones((n, )) * rd
        shape = np.ones((n, )) * shape
        if Nd is None:
            if volfrac is None:
                raise TypeError('`volfrac` must be given if `Nd` is None')
            if rmean is None:
                if n == 1:
                    rmean = rd if np.isscalar(rd) else rd[0]
                else:
                    raise TypeError('`rmean` must be given if `Nd` is None')
            if rstd is None:
                rstd = 0.2 * rmean
            # XXX - here we assume spherical particles
            #       A better approach is to define volume V(r) and surface
            #       area S(r) as functions of size parameter r.  `shape`
            #       may be used as a simplified way to specify S(r).
            Vd = 4 * pi / 3 * rd ** 3
            x = rd / rmean
            if len(x) > 1:
                b = np.concatenate(([(3 * x[0] - x[1]) / 2],
                                    (x[1:] + x[:-1]) / 2,
                                    [(3 * x[-1] - x[-2]) / 2]))
                dx = np.diff(b)
            else:
                dx = rstd / rmean

            if distribution == 'lognormal':
                sigma2 = np.log(1 + rstd ** 2 / rmean ** 2)
                f = 1 / (np.sqrt(2 * np.pi * sigma2) * x) * np.exp(
                    -(np.log(x) + sigma2 / 2)**2 / (2 * sigma2))
            elif distribution == 'LSW':
                f = (4 / 9 * x ** 2 * (3 / (3 + x)) ** (7 / 3) *
                     (1.5 / (1.5 - x)) ** (11 / 3) * np.exp(x / (x - 1.5)))
                f[x >= 1.5] = 0
            elif distribution == 'gamma':
                k = (rmean / rstd) ** 2
                theta = 1 / k
                f = x ** (k - 1) / (math.gamma(k) * theta ** k) * np.exp(
                    -x / theta)
            elif distribution == 'exp':
                f = np.exp(-x)
            else:
                raise TypeError('unknown distribution:', distribution)

            partdens = volfrac / np.sum(f * dx * Vd)
            Nd = partdens * f * dx

        # Make a copy of self such that we can restore if anything fails
        copy = self.__dict__.copy()
        atvol_ = self.atvol.copy()

        # Set self
        self.phases = np.concatenate((self.phases, [name]))
        self.Xd = np.vstack((self.Xd, Xp))
        self.rd = np.concatenate((self.rd, rd))
        self.shape = np.concatenate((self.shape, shape))
        self.Nd = np.concatenate((self.Nd, np.ones((n, )) * Nd))
        self.phasenames = np.concatenate((self.phasenames, n * [name]))
        if atvol:
            self.atvol = np.concatenate((self.atvol, np.ones((n, )) * atvol))
        else:
            self.atvol = np.concatenate((self.atvol, np.zeros((n, ))))
            self.atvol[-n:] = self.estimated_atvol()[-n:]

        # Check if any site fraction become negative
        Xp_ = self.get_Xp()
        if Xp_.min() < 0 or Xp_.max() > 1:
            if reduce_volfrac:
                warnings.warn(
                    'not enough solute - reducing volume fraction of '
                    'phase %r' % name)
                Nd0 = np.zeros(shape=(n, ))
                Nd1 = Nd
                Ndtol = 1e-7 * Nd1
                assert np.all(Nd1 >= Nd0)
                while np.all(Nd1 - Nd0 > Ndtol):
                    Nd = 0.5 * (Nd0 + Nd1)
                    self.Nd[-n:] = Nd
                    Xp_ = self.get_Xp()
                    if Xp_.min() < 0 or Xp_.max() > 1:
                        Nd1 = Nd
                    else:
                        Nd0 = Nd
                if Xp_.min() < 0 or Xp_.max() > 1:
                    self.Nd[-n:] = Nd0

                Xp_ = self.get_Xp()
                assert Xp_.min() >= 0 and Xp_.max() <= 1
            else:
                self.__dict__.update(copy)
                self.atvol = atvol_
                raise NotEnoughSoluteError(
                    'not enough solute to add phase %r' % name)

    def del_phase(self, name):
        """Removes the given phase.  `name` may either be a name of a phase or
        its index.  Matrix cannot be deleted."""
        i = name if isinstance(name, int) else self.phases.tolist().index(name)
        mask = self.phaseindices != i
        self.phases = self.phases[np.arange(len(self.phases)) != i]
        self.Xd = self.Xd[mask]
        self.rd = self.rd[mask]
        self.shape = self.shape[mask]
        self.Nd = self.Nd[mask]
        self.phasenames = self.phasenames[mask]
        self.atvol = self.atvol[mask]

    def add_primary(self, name='primary', rd=1e-6, shape=1.0,
                    atvol=1.44e-29):
        """This method adds a primary phase roughly corresponding to what
        you will find after homogenisation of Mn-containing Al-Mg-Si alloys.

        If there are no phases with name `name`, a new phase will be added.
        Otherwise the specified phase will be updated.

        See add_particle() for a description of arguments.

        The model is based on the rule of thumb that:
          - all available Fe
          - half of the available Mn
          - the amount of Si corresponding to 0.33*(C0_Fe + 0.5*C0_Mn)
        is consumed by the primary particles [Myhr2015]. Furthermore
        is an alpha-like composition imposed, which limits the maximum
        volume fraction.
        """
        for e in ('Al', 'Si', 'Mn', 'Fe'):
            if not e in self.elements:
                #raise KeyError('missing element: %s' % e)
                print("Warning missing element: %s" % e)
                return
        ie = {e: i for i, e in enumerate(self.elements)}
        iFe = ie['Fe']
        iMn = ie['Mn']
        iSi = ie['Si']
        iAl = ie['Al']
        M = [molar_masses[atomic_numbers[e]] for e in self.elements]
        alphass = self.alpha[0]
        alpha = self.atvol0 / atvol
        fss = self.volfrac[0]
        Xss = self.Xss
        xFe = fss * alphass / alpha * Xss[iFe]
        xMn = 0.5 * fss * alphass / alpha * Xss[iMn]
        xSi = fss * alphass * (Xss[iFe] * M[iFe] + 0.5 * Xss[iMn] * M[iMn]) / (
            3 * M[iSi] * alpha)
        xSiAl = 114 / 24 * (xFe + xMn)
        Xp = np.zeros((self.nelements, ))
        Xp[iFe] = 24 / 138 * xFe / (xFe + xMn)
        Xp[iMn] = 24 / 138 * xMn / (xFe + xMn)
        Xp[iSi] = 114 / 138 * xSi / xSiAl
        Xp[iAl] = 1 - Xp[iFe] - Xp[iMn] - Xp[iSi]
        volfrac = min(xFe / Xp[iFe], xMn / Xp[iMn], xSi / Xp[iSi])

        if name in self.phases:
            mask = self.phasenames == name
            self.Xd[mask] = Xp
            self.rd[mask] = rd
            self.shape[mask] = shape
            Vd = 4 * pi / 3 * np.array(rd) ** 3
            self.Nd[mask] = np.array([volfrac / Vd])
            self.atvol[mask] = atvol
        else:
            self.add_phase(name, Xp, rd, volfrac=volfrac, shape=shape,
                           atvol=atvol)

    def plot_partdist(self, fig=None, title=None, phases=None, labels=None):
        """Plots particle distribution for selected phases and returns a
        matplotlib figure instance.

        Parameters
        ----------
        fig : matplotlib.pyplot.figure instance
            Figure to plot to. If None, a new figure is created.
        title : string
            Figure title.
        phases : sequence
            Name of phases to plot.  Defaults to all but the first phase
            (matrix).
        labels : sequence
            Sequence of labels corresponding to `phases`.  Default to
            phase names.
        """
        if fig is None:
            fig = plt.figure()
        ax = fig.gca()
        if phases is None:
            phases = self.phases[1:]
        if labels is None:
            labels = phases
        for phase, label in zip(phases, labels):
            mask = self.phasenames == phase
            ax.plot(1e9 * self.rd[mask], self.Nd[mask], label=label)
        ax.set_xlabel('Particle size (nm)')
        ax.set_ylabel(u'Number density (#/m³)')
        if title is not None:
            ax.set_title(title)
        ax.legend(loc='best')
        return fig


class Chemistry(BaseChemistry):
    """Class describing the alloy composition and particle size distribution.

    Parameters
    ----------
    elements : sequence of strings
        Chemical symbol of each chemical element.  By convension the
        dependent element (e.g. Al) is listed first.
        Required if `uuid` is not given; [nelements]
    phases : sequence of strings
        Name of phases.  Matrix should be listed first.
        Required if `uuid` is not given; [nphases]
    X0 : sequence of floats
        Nominal alloy composition.
        Required if `uuid` is not given; [nelements], atom-fractions
    uuid : string
        UUID of SOFT instance to initialise values from. Requires softpy.
    driver : None | "json" | "hdf5" | "mongo" | ...
        The driver to use for loading initial values.  Requires softpy.
    uri : string
        URI to initial values.  Requires softpy.
    options : None | string
        Additional options passed to the driver.
    **kwargs :
        Additional keyword arguments passed to SOFT initialiser.

    Note
    ----
    This class should confirm to the SOFT entity Chemistry version 0.1.
    We refer to that for a description of attributes.
    """

    # This class is implemented as an adaptor that delegates most of
    # its implementation to an underlying ChemistrySizeDistribution
    # instance
    #
    # The following attributes, properties and methods are deligated
    _deligated = [
        'elements', 'phases', 'X0',
        'nelements', 'nphases',
        'partdens', 'alpha', 'Xss', 'C0', 'Cp', 'Css', 'c0', 'cp', 'css',
        'get_alpha', 'get_cp', 'add_primary',
    ]

    def __init__(self, elements=None, phases=None, X0=None,
                 uuid=None, driver=None, uri=None, options=None, **kwargs):
        super(Chemistry, self).__init__(
            uuid=uuid, driver=driver, uri=uri, options=options,
            uninitialize=False)

        # the underlying ChemistrySizeDistribution instance
        if not '_csd' in self.__dict__:
            self.__dict__['_csd'] = ChemistrySizeDistribution(
                elements=elements, phases=phases, X0=X0)

        if elements is not None and phases is not None:
            self._assign_nondeligated_attr()
            self.__init_finalize__()

    def __init_finalize__(self):
        if '_csd' not in self.__dict__:
            self.__dict__['_csd'] = ChemistrySizeDistribution(
                elements=self.elements, phases=self.phases, X0=self.X0)
        csd = self.__dict__['_csd']
        phases = self.phases[:]
        for j in range(1, len(phases)):
            csd.del_phase(phases[j])
            csd.add_phase(
                name=self.phases[j],
                Xp=self.Xp[j],
                rd=[self.rmean[j]],
                volfrac=self.volfrac[j],
                atvol=self.atvol[j])

    def _assign_nondeligated_attr(self):
        """Assigns non-deligated attributes."""
        # manipulate self.__dict__ directly to avoid triggering __setattr__()
        self.__dict__['Xp'] = ca.array(
            self._csd.Xp,
            cb=lambda arr, i, value: self._csd.set_Xp_i(i, value))

        self.__dict__['volfrac'] = ca.array(
            self._csd.volfrac,
            cb=lambda arr, i, value: self._csd.set_volfrac_i(i, value))

        self.__dict__['rmean'] = ca.array(
            self._csd.rmean,
            cb=lambda arr, i, value: self._csd.set_rmean_i(i, value))

        self.__dict__['atvol'] = self._csd.get_atvol('phase')

    def __str__(self):
        return self._csd.__str__()

    def add_phase(self, name, Xp, rd, Nd=None, volfrac=None, atvol=None):
        """Adds a new phase.  See ChemistrySizeDistribution.add_phase()."""
        self._csd.add_phase(name, Xp, rd, volfrac=volfrac, Nd=Nd,
                            atvol=atvol)
        self._assign_nondeligated_attr()

    def del_phase(self, name):
        """Removes the given phase.  See
        ChemistrySizeDistribution.del_phase()."""
        self._csd.del_phase(name)
        self._assign_nondeligated_attr()

    def __getattr__(self, name):
        if name in self._deligated:
            return getattr(self._csd, name)
        else:
            raise AttributeError('%r object has no attribute %r' % (
                self.__class__.__name__, name))

    def __setattr__(self, name, value):
        if name in self._deligated:
            setattr(self._csd, name, value)
        elif name in ('Xp', 'volfrac', 'rmean', 'atvol'):
            arr = getattr(self, name)
            arr[:] = value
        else:
            super(Chemistry, self).__setattr__(name, value)
