# -*- coding: utf-8 -*-
"""This module define some common physical (and mathematical)
constants.  It is not needed for interoperability, but provided for
convenience.

All values are available both as module variables and attributes of Constants.

The values of natural constants are taken from CODATA 2017 [1], from which
will form the basis for the new definitions in the the proposed
revision of the SI system, which will come into force May 20, 2019 [2].

Tabulated molar masses [3] and atomic radii [4-10] are also provided.

References
----------
[1]  D B Newell et al (2018) Metrologia 55 L13,
     https://doi.org/10.1088/1681-7575/aa950a
[2]  https://en.wikipedia.org/wiki/Proposed_redefinition_of_SI_base_units
[3]  Meija, J., Coplen, T., Berglund, M., et al. (2016). Atomic weights of
     the elements 2013 (IUPAC Technical Report). Pure and Applied Chemistry,
     88(3), pp. 265-291. Retrieved 30 Nov. 2016,
     https://doi.org/10.1515/pac-2015-0305
[4]  J.C. Slater (1964). "Atomic Radii in Crystals". J. Chem. Phys. 41:
     3199. Bibcode:1964JChPh..41.3199S. doi:10.1063/1.1725697
[5]  E. Clementi; D.L.Raimondi; W.P. Reinhardt (1967). "Atomic Screening
     Constants from SCF Functions. II. Atoms with 37 to 86 Electrons".
     J. Chem. Phys. 47: 1300. Bibcode:1967JChPh..47.1300C.
     doi:10.1063/1.1712084.
[6]  M. Mantina; A.C. Chamberlin; R. Valero; C.J. Cramer; D.G. Truhlar (2009).
     "Consistent van der Waals Radii for the Whole Main Group".
     J. Phys. Chem. A. 113 (19): 5806-12. doi:10.1021/jp8111556.
[7]  Beatriz Cordero, Verónica Gómez, Ana E. Platero-Prats, Marc Revés,
     Jorge Echeverría, Eduard Cremades, Flavia Barragán and Santiago Alvarez,
     Dalton Trans., 2008, 2832-2838,
     https://doi.org/10.1039/B801115J
[8]  A.M. James & M.P. Lord (1992). Macmillan's Chemical and Physical Data.
     MacMillan. ISBN 0-333-51167-0.
[9]  S. Riedel; P.Pyykkö, M. Patzschke; Patzschke, M (2005).
     "Triple-Bond Covalent Radii". Chem. Eur. J. 11 (12): 3511-3520.
     doi:10.1002/chem.200401299
[10] Greenwood, Norman N.; Earnshaw, Alan (1997). Chemistry of the Elements
     (2nd ed.). Butterworth-Heinemann. ISBN 0-08-037941-9.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np

from calm import get_entity

BaseConstants = get_entity('Constants', '0.1', 'http://www.sintef.no/calm')


__all__ = ('kB', 'NA', 'Rgas', 'c0', 'hPlanck', 'q_e', 'Kcd', 'Dnu_Cd',
           'pi',
           'chemical_symbols', 'atomic_names', 'atomic_numbers',
           'covalent_radii', 'molar_masses')


class Constants(BaseConstants):
    """Some physical (and mathematical) constants.  Only one instance of
    this class is needed.
    """
    def __init__(self, **kwargs):
        super(BaseConstants, self).__init__(**kwargs)
        self.kB = kB
        self.NA = NA
        self.Rgas = Rgas

        self.c0 = c0
        self.hPlanck = hPlanck
        self.q_e = q_e
        self.Kcd = Kcd
        self.Dnu_Cd = self.Dnu_Cd

        self.pi = pi

        self.chemical_symbols = chemical_symbols
        self.molar_masses = molar_masses
        self.covalent_radii = covalent_radii

    atomic_numbers = property(
        lambda self: {s: Z for Z, s in enumerate(self.chemical_symbols)},
        doc='Dict mapping chemical symbol to its atomic number.')


kB = 1.380649e-23         # Boltzmann constant, J/K
NA = 6.02214076e23        # Avogadro constant, 1/mol
Rgas = kB * NA            # gas constant, J/(mol K)

# Other fundamental physical constants, less used in classical
# physical metallurgy
c0 = 299792458            # speed of light in vacuum, m/s
hPlanck = 6.62607015e-34  # Planck constant, kg m^2/s
q_e = 1.602176634e-19     # elementary charge, As
Kcd = 683                 # luminous efficacy of monochromatic radiation of
                          # frequency 540e12 Hz, cd sr s^3/(kg m^2)
Dnu_Cd = 9192631770       # ground state hyperfine splitting frequency of
                          # the caesium-133 atom, 1/s

pi = np.pi


# Atomic radii
# ------------
# r_emp:  Empirical [4]
# r_calc: Calculated [5]
# r_vdw:  Van der Waals [6]
# r_cov:  Covalent [7]
# r_cov2: Covalent, single-bond [8]
# r_cov3: Covalent, triple-bond [9]
# r_met:  Metallic [10]
nan = np.nan
atomic_radii = np.rec.fromrecords([
    # sym   name         r_emp   r_calc  r_vdw r_cov  r_cov2   r_cov3  r_met
    ('X',  'vacancy',      nan,    nan,    nan,  nan,  nan,    nan,    nan),
    ('H',  'hydrogen',     25,     53,     120,   31,  38,     nan,    nan),
    ('He', 'helium',       120,    31,     140,   28,  32,     nan,    nan),
    ('Li', 'lithium',      145,    167,    182,  128,  134,    nan,    152),
    ('Be', 'beryllium',    105,    112,    153,   96,  90,     85,     112),
    ('B',  'boron',        85,     87,     192,   84,  82,     73,     nan),
    ('C',  'carbon',       70,     67,     170,   76,  77,     60,     nan),
    ('N',  'nitrogen',     65,     56,     155,   71,  75,     54,     nan),
    ('O',  'oxygen',       60,     48,     152,   66,  73,     53,     nan),
    ('F',  'fluorine',     50,     42,     147,   57,  71,     53,     nan),
    ('Ne', 'neon',         160,    38,     154,   58,  69,     nan,    nan),
    ('Na', 'sodium',       180,    190,    227,  166,  154,    nan,    186),
    ('Mg', 'magnesium',    150,    145,    173,  141,  130,    127,    160),
    ('Al', 'aluminium',    125,    118,    184,  121,  118,    111,    143),
    ('Si', 'silicon',      110,    111,    210,  111,  111,    102,    nan),
    ('P',  'phosphorus',   100,    98,     180,  107,  106,    94,     nan),
    ('S',  'sulfur',       100,    88,     180,  105,  102,    95,     nan),
    ('Cl', 'chlorine',     100,    79,     175,  102,  99,     93,     nan),
    ('Ar', 'argon',        71,     71,     188,  106,  97,     96,     nan),
    ('K',  'potassium',    220,    243,    275,  203,  196,    nan,    227),
    ('Ca', 'calcium',      180,    194,    231,  176,  174,    133,    197),
    ('Sc', 'scandium',     160,    184,    211,  170,  144,    114,    162),
    ('Ti', 'titanium',     140,    176,    nan,  160,  136,    108,    147),
    ('V',  'vanadium',     135,    171,    nan,  153,  125,    106,    134),
    ('Cr', 'chromium',     140,    166,    nan,  139,  127,    103,    128),
    ('Mn', 'manganese',    140,    161,    nan,  139,  139,    103,    127),
    ('Fe', 'iron',         140,    156,    nan,  132,  125,    102,    126),
    ('Co', 'cobalt',       135,    152,    nan,  126,  126,    96,     125),
    ('Ni', 'nickel',       135,    149,    163,  124,  121,    101,    124),
    ('Cu', 'copper',       135,    145,    140,  132,  138,    120,    128),
    ('Zn', 'zinc',         135,    142,    139,  122,  131,    nan,    134),
    ('Ga', 'gallium',      130,    136,    187,  122,  126,    121,    135),
    ('Ge', 'germanium',    125,    125,    211,  120,  122,    114,    nan),
    ('As', 'arsenic',      115,    114,    185,  119,  119,    106,    nan),
    ('Se', 'selenium',     115,    103,    190,  120,  116,    107,    nan),
    ('Br', 'bromine',      115,    94,     185,  120,  114,    110,    nan),
    ('Kr', 'krypton',      nan,    88,     202,  116,  110,    108,    nan),
    ('Rb', 'rubidium',     235,    265,    303,  220,  211,    nan,    248),
    ('Sr', 'strontium',    200,    219,    249,  195,  192,    139,    215),
    ('Y',  'yttrium',      180,    212,    nan,  190,  162,    124,    180),
    ('Zr', 'zirconium',    155,    206,    nan,  175,  148,    121,    160),
    ('Nb', 'niobium',      145,    198,    nan,  164,  137,    116,    146),
    ('Mo', 'molybdenum',   145,    190,    nan,  154,  145,    113,    139),
    ('Tc', 'technetium',   135,    183,    nan,  147,  156,    110,    136),
    ('Ru', 'ruthenium',    130,    178,    nan,  146,  126,    103,    134),
    ('Rh', 'rhodium',      135,    173,    nan,  142,  135,    106,    134),
    ('Pd', 'palladium',    140,    169,    163,  139,  131,    112,    137),
    ('Ag', 'silver',       160,    165,    172,  145,  153,    137,    144),
    ('Cd', 'cadmium',      155,    161,    158,  144,  148,    nan,    151),
    ('In', 'indium',       155,    156,    193,  142,  144,    146,    167),
    ('Sn', 'tin',          145,    145,    217,  139,  141,    132,    nan),
    ('Sb', 'antimony',     145,    133,    206,  139,  138,    127,    nan),
    ('Te', 'tellurium',    140,    123,    206,  138,  135,    121,    nan),
    ('I',  'iodine',       140,    115,    198,  139,  133,    125,    nan),
    ('Xe', 'xenon',        nan,    108,    216,  140,  130,    122,    nan),
    ('Cs', 'caesium',      260,    298,    343,  244,  225,    nan,    265),
    ('Ba', 'barium',       215,    253,    268,  215,  198,    149,    222),
    ('La', 'lanthanum',    195,    nan,    nan,  207,  169,    139,    187),
    ('Ce', 'cerium',       185,    nan,    nan,  204,  nan,    131,    181.8),
    ('Pr', 'praseodymium', 185,    247,    nan,  203,  nan,    128,    182.4),
    ('Nd', 'neodymium',    185,    206,    nan,  201,  nan,    nan,    181.4),
    ('Pm', 'promethium',   185,    205,    nan,  199,  nan,    nan,    183.4),
    ('Sm', 'samarium',     185,    238,    nan,  198,  nan,    nan,    180.4),
    ('Eu', 'europium',     185,    231,    nan,  198,  nan,    nan,    180.4),
    ('Gd', 'gadolinium',   180,    233,    nan,  196,  nan,    132,    180.4),
    ('Tb', 'terbium',      175,    225,    nan,  194,  nan,    nan,    177.3),
    ('Dy', 'dysprosium',   175,    228,    nan,  192,  nan,    nan,    178.1),
    ('Ho', 'holmium',      175,    nan,    nan,  192,  nan,    nan,    176.2),
    ('Er', 'erbium',       175,    226,    nan,  189,  nan,    nan,    176.1),
    ('Tm', 'thulium',      175,    222,    nan,  190,  nan,    nan,    175.9),
    ('Yb', 'ytterbium',    175,    222,    nan,  187,  nan,    nan,    176),
    ('Lu', 'lutetium',     175,    217,    nan,  187,  160,    131,    173.8),
    ('Hf', 'hafnium',      155,    208,    nan,  175,  150,    122,    159),
    ('Ta', 'tantalum',     145,    200,    nan,  170,  138,    119,    146),
    ('W',  'tungsten',     135,    193,    nan,  162,  146,    115,    139),
    ('Re', 'rhenium',      135,    188,    nan,  151,  159,    110,    137),
    ('Os', 'osmium',       130,    185,    nan,  144,  128,    109,    135),
    ('Ir', 'iridium',      135,    180,    nan,  141,  137,    107,    135.5),
    ('Pt', 'platinum',     135,    177,    175,  136,  128,    110,    138.5),
    ('Au', 'gold',         135,    174,    166,  136,  144,    123,    144),
    ('Hg', 'mercury',      150,    171,    155,  132,  149,    nan,    151),
    ('Tl', 'thallium',     190,    156,    196,  145,  148,    150,    170),
    ('Pb', 'lead',         180,    154,    202,  146,  147,    137,    nan),
    ('Bi', 'bismuth',      160,    143,    207,  148,  146,    135,    nan),
    ('Po', 'polonium',     190,    135,    197,  140,  nan,    129,    nan),
    ('At', 'astatine',     nan,    nan,    202,  150,  nan,    138,    nan),
    ('Rn', 'radon',        nan,    120,    220,  150,  145,    133,    nan),
    ('Fr', 'francium',     nan,    nan,    348,  260,  nan,    nan,    nan),
    ('Ra', 'radium',       215,    nan,    283,  221,  nan,    159,    nan),
    ('Ac', 'actinium',     195,    nan,    nan,  215,  nan,    140,    nan),
    ('Th', 'thorium',      180,    nan,    nan,  206,  nan,    136,    179),
    ('Pa', 'protactinium', 180,    nan,    nan,  200,  nan,    129,    163),
    ('U',  'uranium',      175,    nan,    186,  196,  nan,    118,    156),
    ('Np', 'neptunium',    175,    nan,    nan,  190,  nan,    116,    155),
    ('Pu', 'plutonium',    175,    nan,    nan,  187,  nan,    nan,    159),
    ('Am', 'americium',    175,    nan,    nan,  180,  nan,    nan,    173),
    ('Cm', 'curium',       nan,    nan,    nan,  169,  nan,    nan,    174),
    ('Bk', 'berkelium',    nan,    nan,    nan,  nan,  nan,    nan,    170),
    ('Cf', 'californium',  nan,    nan,    nan,  nan,  nan,    nan,    186),
    ('Es', 'einsteinium',  nan,    nan,    nan,  nan,  nan,    nan,    186),
    ('Fm', 'fermium',      nan,    nan,    nan,  nan,  nan,    nan,    nan),
    ('Md', 'mendelevium',  nan,    nan,    nan,  nan,  nan,    nan,    nan),
    ('No', 'nobelium',     nan,    nan,    nan,  nan,  nan,    nan,    nan),
    ('Lr', 'lawrencium',   nan,    nan,    nan,  nan,  nan,    nan,    nan),
    ('Rf', 'rutherfordium',nan,    nan,    nan,  nan,  nan,    131,    nan),
    ('Db', 'dubnium',      nan,    nan,    nan,  nan,  nan,    126,    nan),
    ('Sg', 'seaborgium',   nan,    nan,    nan,  nan,  nan,    121,    nan),
    ('Bh', 'bohrium',      nan,    nan,    nan,  nan,  nan,    119,    nan),
    ('Hs', 'hassium',      nan,    nan,    nan,  nan,  nan,    118,    nan),
    ('Mt', 'meitnerium',   nan,    nan,    nan,  nan,  nan,    113,    nan),
    ('Ds', 'darmstadtium', nan,    nan,    nan,  nan,  nan,    112,    nan),
    ('Rg', 'roentgenium',  nan,    nan,    nan,  nan,  nan,    118,    nan),
    ('Cn', 'copernicium',  nan,    nan,    nan,  nan,  nan,    130,    nan),
    ('Nh', 'nihonium',     nan,    nan,    nan,  nan,  nan,    nan,    nan),
    ('Fl', 'flerovium',    nan,    nan,    nan,  nan,  nan,    nan,    nan),
    ('Mc', 'moscovium',    nan,    nan,    nan,  nan,  nan,    nan,    nan),
    ('Lv', 'livermorium',  nan,    nan,    nan,  nan,  nan,    nan,    nan),
    ('Ts', 'tennessine',   nan,    nan,    nan,  nan,  nan,    nan,    nan),
    ('Og', 'oganesson',    nan,    nan,    nan,  nan,  nan,    nan,    nan),
], names='symbols,names,r_emp,r_calc,r_vdw,r_cov,r_cov2,r_cov3,r_met')

chemical_symbols = atomic_radii['symbols']
atomic_names = atomic_radii['names']
atomic_numbers = {s: Z for Z, s in enumerate(chemical_symbols)}
covalent_radii = 1e-12 * atomic_radii['r_cov']


# Standard atomic weights in kg/mol are taken from Table 1: "Standard
# atomic weights 2013" in Ref. [4], with the uncertainties ignored.
# For hydrogen, helium, boron, carbon, nitrogen, oxygen, magnesium, silicon,
# sulfur, chlorine, bromine and thallium, where the weights are given as a
# range the "conventional" weights are taken from Table 3 and the ranges are
# given in the comments.
# The mass of the most stable isotope (in Table 4) is used for elements
# where there the element has no stable isotopes (to avoid NaNs): Tc, Pm,
# Po, At, Rn, Fr, Ra, Ac, everything after Np
molar_masses = 1e-3 * np.array([  # kg/mol
    0.0,  # X
    1.008,  # H [1.00784, 1.00811]
    4.002602,  # He
    6.94,  # Li [6.938, 6.997]
    9.0121831,  # Be
    10.81,  # B [10.806, 10.821]
    12.011,  # C [12.0096, 12.0116]
    14.007,  # N [14.00643, 14.00728]
    15.999,  # O [15.99903, 15.99977]
    18.998403163,  # F
    20.1797,  # Ne
    22.98976928,  # Na
    24.305,  # Mg [24.304, 24.307]
    26.9815385,  # Al
    28.085,  # Si [28.084, 28.086]
    30.973761998,  # P
    32.06,  # S [32.059, 32.076]
    35.45,  # Cl [35.446, 35.457]
    39.948,  # Ar
    39.0983,  # K
    40.078,  # Ca
    44.955908,  # Sc
    47.867,  # Ti
    50.9415,  # V
    51.9961,  # Cr
    54.938044,  # Mn
    55.845,  # Fe
    58.933194,  # Co
    58.6934,  # Ni
    63.546,  # Cu
    65.38,  # Zn
    69.723,  # Ga
    72.630,  # Ge
    74.921595,  # As
    78.971,  # Se
    79.904,  # Br [79.901, 79.907]
    83.798,  # Kr
    85.4678,  # Rb
    87.62,  # Sr
    88.90584,  # Y
    91.224,  # Zr
    92.90637,  # Nb
    95.95,  # Mo
    97.90721,  # 98Tc
    101.07,  # Ru
    102.90550,  # Rh
    106.42,  # Pd
    107.8682,  # Ag
    112.414,  # Cd
    114.818,  # In
    118.710,  # Sn
    121.760,  # Sb
    127.60,  # Te
    126.90447,  # I
    131.293,  # Xe
    132.90545196,  # Cs
    137.327,  # Ba
    138.90547,  # La
    140.116,  # Ce
    140.90766,  # Pr
    144.242,  # Nd
    144.91276,  # 145Pm
    150.36,  # Sm
    151.964,  # Eu
    157.25,  # Gd
    158.92535,  # Tb
    162.500,  # Dy
    164.93033,  # Ho
    167.259,  # Er
    168.93422,  # Tm
    173.054,  # Yb
    174.9668,  # Lu
    178.49,  # Hf
    180.94788,  # Ta
    183.84,  # W
    186.207,  # Re
    190.23,  # Os
    192.217,  # Ir
    195.084,  # Pt
    196.966569,  # Au
    200.592,  # Hg
    204.38,  # Tl [204.382, 204.385]
    207.2,  # Pb
    208.98040,  # Bi
    208.98243,  # 209Po
    209.98715,  # 210At
    222.01758,  # 222Rn
    223.01974,  # 223Fr
    226.02541,  # 226Ra
    227.02775,  # 227Ac
    232.0377,  # Th
    231.03588,  # Pa
    238.02891,  # U
    237.04817,  # 237Np
    244.06421,  # 244Pu
    243.06138,  # 243Am
    247.07035,  # 247Cm
    247.07031,  # 247Bk
    251.07959,  # 251Cf
    252.0830,  # 252Es
    257.09511,  # 257Fm
    258.09843,  # 258Md
    259.1010,  # 259No
    262.110,  # 262Lr
    267.122,  # 267Rf
    268.126,  # 268Db
    271.134,  # 271Sg
    270.133,  # 270Bh
    269.1338,  # 269Hs
    278.156,  # 278Mt
    281.165,  # 281Ds
    281.166,  # 281Rg
    285.177,  # 285Cn
    286.182,  # 286Nh
    289.190,  # 289Fl
    289.194,  # 289Mc
    293.204,  # 293Lv
    293.208,  # 293Ts
    294.214,  # 294Og
])
