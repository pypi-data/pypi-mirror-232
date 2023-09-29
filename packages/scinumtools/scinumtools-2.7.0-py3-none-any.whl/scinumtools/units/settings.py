import numpy as np
from enum import Enum, auto

from ..parameter_table import ParameterTable
from ..row_collector import RowCollector
from .unit_types import *
from .unit_list import *

MAGNITUDE_PRECISION = 1e-7

SYMBOL_UNITID   = ":"
SYMBOL_FRACTION = ":"
SYMBOL_MULTIPLY = "*"

UNIT_TYPES = [
    TemperatureUnitType,
    LogarithmicUnitType,
    StandardUnitType,
]

UNIT_PREFIXES = ParameterTable(['magnitude','dimensions','definition','name','prefixes'], {
'Y':        (1.0e24,         [ 0, 0, 0, 0, 0, 0, 0, 0],  '1e24',                   'yotta'            ), 
'Z':        (1.0e21,         [ 0, 0, 0, 0, 0, 0, 0, 0],  '1e21',                   'zetta'            ), 
'E':        (1.0e18,         [ 0, 0, 0, 0, 0, 0, 0, 0],  '1e18',                   'exa'              ), 
'P':        (1.0e15,         [ 0, 0, 0, 0, 0, 0, 0, 0],  '1e15',                   'peta'             ), 
'T':        (1.0e12,         [ 0, 0, 0, 0, 0, 0, 0, 0],  '1e12',                   'tera'             ), 
'G':        (1.0e9,          [ 0, 0, 0, 0, 0, 0, 0, 0],  '1e9',                    'giga'             ), 
'M':        (1.0e6,          [ 0, 0, 0, 0, 0, 0, 0, 0],  '1e6',                    'mega'             ), 
'k':        (1.0e3,          [ 0, 0, 0, 0, 0, 0, 0, 0],  '1e3',                    'kilo'             ), 
'h':        (1.0e2,          [ 0, 0, 0, 0, 0, 0, 0, 0],  '1e2',                    'hecto'            ), 
'da':       (1.0e1,          [ 0, 0, 0, 0, 0, 0, 0, 0],  '1e1',                    'deka'             ), 
'd':        (1.0e-1,         [ 0, 0, 0, 0, 0, 0, 0, 0],  '1e-1',                   'deci'             ), 
'c':        (1.0e-2,         [ 0, 0, 0, 0, 0, 0, 0, 0],  '1e-2',                   'centi'            ), 
'm':        (1.0e-3,         [ 0, 0, 0, 0, 0, 0, 0, 0],  '1e-3',                   'milli'            ), 
'u':        (1.0e-6,         [ 0, 0, 0, 0, 0, 0, 0, 0],  '1e-6',                   'micro'            ), 
'n':        (1.0e-9,         [ 0, 0, 0, 0, 0, 0, 0, 0],  '1e-9',                   'nano'             ), 
'p':        (1.0e-12,        [ 0, 0, 0, 0, 0, 0, 0, 0],  '1e-12',                  'pico'             ), 
'f':        (1.0e-15,        [ 0, 0, 0, 0, 0, 0, 0, 0],  '1e-15',                  'femto'            ), 
'a':        (1.0e-18,        [ 0, 0, 0, 0, 0, 0, 0, 0],  '1e-18',                  'atto'             ), 
'z':        (1.0e-21,        [ 0, 0, 0, 0, 0, 0, 0, 0],  '1e-21',                  'zepto'            ), 
'y':        (1.0e-24,        [ 0, 0, 0, 0, 0, 0, 0, 0],  '1e-24',                  'yocto'            ), 
}, keys=True)
    
UNIT_STANDARD = ParameterTable(['magnitude','dimensions','definition','name','prefixes'], {
# base physical units
'm':        (1.0,            [ 1, 0, 0, 0, 0, 0, 0, 0],  None,                     'meter',             True               ),
'g':        (1.0,            [ 0, 1, 0, 0, 0, 0, 0, 0],  None,                     'gram',              True               ),
's':        (1.0,            [ 0, 0, 1, 0, 0, 0, 0, 0],  None,                     'second',            True               ),
'K':        (1.0,            [ 0, 0, 0, 1, 0, 0, 0, 0],  None,                     'kelvin',            True               ),
'C':        (1.0,            [ 0, 0, 0, 0, 1, 0, 0, 0],  None,                     'coulomb',           True               ),
'cd':       (1.0,            [ 0, 0, 0, 0, 0, 1, 0, 0],  None,                     'candela',           True               ),
# base numerical units
'mol':      (1.0,            [ 0, 0, 0, 0, 0, 0, 1, 0],  None,                     'mole',              True               ),
'rad':      (1.0,            [ 0, 0, 0, 0, 0, 0, 0, 1],  None,                     'radian',            ['m']              ),

# units of distance
'mi':       (1609.344,       [ 1, 0, 0, 0, 0, 0, 0, 0],  '1609.344*m',             'intern. mile',      False              ),
'au':       (1.49597870e11,  [ 1, 0, 0, 0, 0, 0, 0, 0],  '149597.870691*Mm',       'astr. unit',        False              ),
'AU':       (1.49597870e11,  [ 1, 0, 0, 0, 0, 0, 0, 0],  'au',                     'astr. unit',        False              ),
'ly':       (9.460730e15,    [ 1, 0, 0, 0, 0, 0, 0, 0],  '[c]*yr_j',               'light-year',        ['k','M','G']      ),
'pc':       (3.0857e16,      [ 1, 0, 0, 0, 0, 0, 0, 0],  '3.0857e16*m',            'parsec',            ['k','M','G','T']  ),
'Ao':       (1e-10,          [ 1, 0, 0, 0, 0, 0, 0, 0],  '1e-10*m',                'Angstrom',          ['m','k']          ),
# units of mass
'u':        (1.6605402e-24,  [ 0, 1, 0, 0, 0, 0, 0, 0],  '1.6605402e-24*g',        'atomic mass unit',  False              ),
'amu':      (1.6605402e-24,  [ 0, 1, 0, 0, 0, 0, 0, 0],  'u',                      'atomic mass unit',  False              ),
'Da':       (1.6605402e-24,  [ 0, 1, 0, 0, 0, 0, 0, 0],  'u',                      'Dalton',            False              ),
't':        (1e6,            [ 0, 1, 0, 0, 0, 0, 0, 0],  '1e3*kg',                 'tonne',             ['k','m','G']      ),
# units of time
'min':      (6.0e1,          [ 0, 0, 1, 0, 0, 0, 0, 0],  '60*s',                   'minute',            False              ),
'h':        (3.6e3,          [ 0, 0, 1, 0, 0, 0, 0, 0],  '60*min',                 'hour',              False              ),
'day':      (8.64e4,         [ 0, 0, 1, 0, 0, 0, 0, 0],  '24*h',                   'day',               False              ),
'yr_t':     (3.1556925e7,    [ 0, 0, 1, 0, 0, 0, 0, 0],  '365.24219*day',          'tropical year',     ['k','m','G']      ),
'yr_j':     (3.1557600e7,    [ 0, 0, 1, 0, 0, 0, 0, 0],  '365.25*day',             'Julian year',       ['k','m','G']      ),
'yr_g':     (3.155695e7,     [ 0, 0, 1, 0, 0, 0, 0, 0],  '365.2425*day',           'Gregorian year',    ['k','m','G']      ),
'yr':       (3.155760e7,     [ 0, 0, 1, 0, 0, 0, 0, 0],  'yr_j',                   'year',              ['k','m','G']      ),
# units of temperature
'degR':     (5/9,            [ 0, 0, 0, 1, 0, 0, 0, 0],  '5/9*K',                  'degree Rankine',    False              ),
'Cel':      (1,              [ 0, 0, 0, 1, 0, 0, 0, 0],  TemperatureUnitType,      'degree Celsius',    False              ),
'degF':     (1,              [ 0, 0, 0, 1, 0, 0, 0, 0],  TemperatureUnitType,      'degree Fahrenheit', False              ),
# angular units
'deg':      (1.7453292e-2,   [ 0, 0, 0, 0, 0, 0, 0, 1],  '2*[pi]*rad/360',         'angle degree',      False              ),
"'":        (2.908882e-4,    [ 0, 0, 0, 0, 0, 0, 0, 1],  'deg/60',                 'angle minute',      False              ),
"''":       (4.848137e-6,    [ 0, 0, 0, 0, 0, 0, 0, 1],  "'/60",                   'angle second',      False              ),

# units of surface
'ar':       (1.0e2,          [ 2, 0, 0, 0, 0, 0, 0, 0],  '100*m2',                 'are',               ['c','d','da','h'] ),
# units of volume
'l':        (1e-3,           [ 3, 0, 0, 0, 0, 0, 0, 0],  'dm3',                    'liter',             False              ),
'L':        (1e-3,           [ 3, 0, 0, 0, 0, 0, 0, 0],  'l',                      'liter',             False              ),
# units of energy
'J':        (1.0e3,          [ 2, 1,-2, 0, 0, 0, 0, 0],  'N*m',                    'joule',             True               ),
'eV':       (1.60217733e-16, [ 2, 1,-2, 0, 0, 0, 0, 0],  '[e]*V',                  'electronvolt',      True               ),
'erg':      (1.0e-4,         [ 2, 1,-2, 0, 0, 0, 0, 0],  'dyn*cm',                 'erg',               False              ),
'Ha':       (4.35974472e-15, [ 2, 1,-2, 0, 0, 0, 0, 0],  '4.3597447222071e-18*J',  'Hartree',           ['k','M']          ),
'E_h':      (4.35974472e-15, [ 2, 1,-2, 0, 0, 0, 0, 0],  'Ha',                     'Hartree',           ['k','M']          ),
# units of pressure
'Pa':       (1.0e3,          [-1, 1,-2, 0, 0, 0, 0, 0],  'N/m2',                   'pascal',            True               ),
'atm':      (1.013250e8,     [-1, 1,-2, 0, 0, 0, 0, 0],  '101325*Pa',              'atm. pressure',     False              ),
'bar':      (1e8,            [-1, 1,-2, 0, 0, 0, 0, 0],  '100*kPa',                'bar',               ['m']              ),
'Ba':       (1e2,            [-1, 1,-2, 0, 0, 0, 0, 0],  '0.1*Pa',                 'Barye',             False              ),
# units of force
'N':        (1.0e3,          [ 1, 1,-2, 0, 0, 0, 0, 0],  'kg*m/s2',                'newton',            True               ),
'dyn':      (1.0e-2,         [ 1, 1,-2, 0, 0, 0, 0, 0],  'g*cm/s2',                'dyne',              True               ),
# units of energy absorption
'Gy':       (1.0e0,          [ 2, 0,-2, 0, 0, 0, 0, 0],  'J/kg',                   'gray',              False              ),
'Sv':       (1.0e0,          [ 2, 0,-2, 0, 0, 0, 0, 0],  'J/kg',                   'sivert',            False              ),
# units of magnetic flux density
'T':        (1.0e3,          [ 0, 1,-1, 0,-1, 0, 0, 0],  'Wb/m2',                  'tesla',             True               ),
'G':        (1.0e-1,         [ 0, 1,-1, 0,-1, 0, 0, 0],  '1e-4*T',                 'Gauss',             True               ),
# units of frequency
'Hz':       (1.0e0,          [ 0, 0,-1, 0, 0, 0, 0, 0],  's-1',                    'hertz',             True               ),
'Bq':       (1.0e0,          [ 0, 0,-1, 0, 0, 0, 0, 0],  's-1',                    'becquerel',         False              ),

# other derived units              
'sr':       (1.0e0,          [ 0, 0, 0, 0, 0, 0, 0, 2],  'rad2',                   'steradian',         False              ),
'lm':       (1.0e0,          [ 0, 0, 0, 0, 0, 1, 0, 2],  'cd*sr',                  'lumen',             False              ),
'A':        (1.0e0,          [ 0, 0,-1, 0, 1, 0, 0, 0],  'C/s',                    'ampere',            True               ),
'H':        (1.0e3,          [ 2, 1, 0, 0,-2, 0, 0, 0],  'Wb/A',                   'henry',             False              ),
'Ohm':      (1.0e3,          [ 2, 1,-1, 0,-2, 0, 0, 0],  'V/A',                    'ohm',               True               ),
'Wb':       (1.0e3,          [ 2, 1,-1, 0,-1, 0, 0, 0],  'V*s',                    'weber',             False              ),
'V':        (1.0e3,          [ 2, 1,-2, 0,-1, 0, 0, 0],  'J/C',                    'volt',              True               ),
'W':        (1.0e3,          [ 2, 1,-3, 0, 0, 0, 0, 0],  'J/s',                    'watt',              True               ),
'lx':       (1.0e0,          [-2, 0, 0, 0, 0, 1, 0, 2],  'lm/m2',                  'lux',               False              ),
'F':        (1.0e-3,         [-2,-1, 2, 0, 2, 0, 0, 0],  'C/V',                    'farad',             True               ),
'S':        (1.0e-3,         [-2,-1, 1, 0, 2, 0, 0, 0],  'Ohm-1',                  'siemens',           True               ),
'kat':      (1,              [ 0, 0,-1, 0, 0, 0, 1, 0],  'mol/s',                  'katal',             True               ),
'D':        (3.33564e-30,    [ 1, 0, 0, 0, 1, 0, 0, 0],  '3.33564e-30*C*m',        'Debye',             True               ),
# logarithmic units and ratios
'PR':       (1,              [ 0, 0, 0, 0, 0, 0, 0, 0],  '1',                      'Power ratio',       False              ), 
'AR':       (1,              [ 0, 0, 0, 0, 0, 0, 0, 0],  '1',                      'Amplitude ratio',   False              ),
'Np':       (1,              [ 0, 0, 0, 0, 0, 0, 0, 0],  LogarithmicUnitType,      'Nepers',            ['c','d']          ),
'B':        (1,              [ 0, 0, 0, 0, 0, 0, 0, 0],  LogarithmicUnitType,      'Bel',               ['d']              ),
'Bm':       (1,              [ 2, 1,-3, 0, 0, 0, 0, 0],  LogarithmicUnitType,      'bel-milliwatt',     ['d']              ),
'BmW':      (1,              [ 2, 1,-3, 0, 0, 0, 0, 0],  LogarithmicUnitType,      'bel-milliwatt',     ['d']              ),
'BW':       (1,              [ 2, 1,-3, 0, 0, 0, 0, 0],  LogarithmicUnitType,      'bel-watt',          ['d']              ),
'BV':       (1,              [ 2, 1,-2, 0,-1, 0, 0, 0],  LogarithmicUnitType,      'bel-volt',          ['d']              ),
'BuV':      (1,              [ 2, 1,-2, 0,-1, 0, 0, 0],  LogarithmicUnitType,      'bel-microvolt',     ['d']              ),
'BA':       (1,              [ 0, 0,-1, 0, 1, 0, 0, 0],  LogarithmicUnitType,      'bel-amps',          ['d']              ),
'BuA':      (1,              [ 0, 0,-1, 0, 1, 0, 0, 0],  LogarithmicUnitType,      'bel-microamps',     ['d']              ),
'BOhm':     (1,              [ 2, 1,-1, 0,-2, 0, 0, 0],  LogarithmicUnitType,      'bel-ohms',          ['d']              ),
'BSPL':     (1,              [-1, 1,-2, 0, 0, 0, 0, 0],  LogarithmicUnitType,      'bel-SPL (Pa)',      ['d']              ),
'BSIL':     (1,              [ 0, 1,-3, 0, 0, 0, 0, 0],  LogarithmicUnitType,      'bel-SIL (W/m2)',    ['d']              ), 
'BSWL':     (1,              [ 2, 1,-3, 0, 0, 0, 0, 0],  LogarithmicUnitType,      'bel-SWL (W)',       ['d']              ),
# percentages
'%':        (1e-2,           [ 0, 0, 0, 0, 0, 0, 0, 0],  '1e-2',                   'percent',           False              ),
'ppth':     (1e-3,           [ 0, 0, 0, 0, 0, 0, 0, 0],  '1e-3',                   'promile',           False              ),
# natural constants    
'[a_0]':    (5.291772109e-11,[ 1, 0, 0, 0, 0, 0, 0, 0],  '5.291772109e-11*m',      'Bohr radius',       False              ),
'[c]':      (2.99792458e8,   [ 1, 0,-1, 0, 0, 0, 0, 0],  '299792458*m/s',          'speed of light',    False              ),
'[e]':      (1.60217733e-19, [ 0, 0, 0, 0, 1, 0, 0, 0],  '1.60217733e-19*C',       'elem. charge',      False              ),
'[eps_0]':  (8.854188e-15,   [-3,-1, 2, 0, 2, 0, 0, 0],  '8.854187817e-12*F/m',    'permit. of vac.',   False              ),
'[G]':      (6.672590e-14,   [ 3,-1,-2, 0, 0, 0, 0, 0],  '6.67259e-11*m3/(kg*s2)', 'grav. const.',      False              ),
'[g]':      (9.806650e0,     [ 1, 0,-2, 0, 0, 0, 0, 0],  '9.80665*m/s2',           'grav. accel.',      False              ),
'[h]':      (6.626076e-31,   [ 2, 1,-1, 0, 0, 0, 0, 0],  '6.6260755e-34*J*s',      'Planck const.',     False              ),
'[hbar]':   (1.054572748e-31,[ 2, 1,-1, 0, 0, 0, 0, 0],  '[h]/(2*[pi])',           'Reduced Pl. con.',  False              ),
'[H_0]':    (2.197232394e-18,[ 0, 0,-1, 0, 0, 0, 0, 0],  '67.8*km/(s*Mpc)',        'Hubble const.',     False              ),
'[k]':      (1.380658e-20,   [ 2, 1,-2,-1, 0, 0, 0, 0],  '1.380658e-23*J/K',       'Boltzmann const.',  False              ),
'[k_B]':    (1.380658e-20,   [ 2, 1,-2,-1, 0, 0, 0, 0],  '[k]',                    'Boltzmann const.',  False              ),
'[L_sol]':  (3.826e29,       [ 2, 1,-3, 0, 0, 0, 0, 0],  '3.826e33*erg/s',         'Solar luminosity',  False              ),
'[M_sol]':  (1.98847e33,     [ 0, 1, 0, 0, 0, 0, 0, 0],  '1.98847e30*kg',          'Solar mass',        False              ),
'[mu_0]':   (1.256637e-3,    [ 1, 1, 0, 0,-2, 0, 0, 0],  '4*[pi]*1e-7*N/A2',       'permeab. of vac.',  False              ),
'[mu_B]':   (1.67262e-24,    [ 0, 1, 0, 0, 0, 0, 0, 0],  '1.67262e-24*g',          'Bohr magneton',     False              ),
'[m_e]':    (9.109390e-28,   [ 0, 1, 0, 0, 0, 0, 0, 0],  '9.1093897e-28*g',        'electron mass',     False              ),
'[m_p]':    (1.672623e-24,   [ 0, 1, 0, 0, 0, 0, 0, 0],  '1.6726231e-24*g',        'proton mass',       False              ),
'[m_n]':    (1.6749286e-24,  [ 0, 1, 0, 0, 0, 0, 0, 0],  '1.6749286e-24*g',        'neutron mass',      False              ),
'[R_inf]':  (1.09737e7,      [-1, 0, 0, 0, 0, 0, 0, 0],  '1.09737e5/cm',           'Rydberg constant',  False              ),
'[R_sol]':  (6.9558e8,       [ 1, 0, 0, 0, 0, 0, 0, 0],  '6.9558e10*cm',           'Solar radius',      False              ),
'[sigma]':  (5.67037e-5,     [ 0, 1,-3,-4, 0, 0, 0, 0],  '5.67037e-8*W/(m2*K4)',   'Stef.-Boltz. const.', False            ),
# dimensionless constants
'[alpha]':  (7.29735256e-3,  [ 0, 0, 0, 0, 0, 0, 0, 0],  '7.29735256e-3',          "fine str. const.",  False              ),
'[euler]':  (np.e,           [ 0, 0, 0, 0, 0, 0, 0, 0],  '2.718282',               "Euler's num.",      False              ),
'[N_A]':    (6.0221367e23,   [ 0, 0, 0, 0, 0, 0, 0, 0],  '6.022137e23',            "Avogadro's num.",   False              ),
'[pi]':     (np.pi,          [ 0, 0, 0, 0, 0, 0, 0, 0],  '3.1415926',              'pi',                False              ),
}, keys=True)

QUANTITY_LIST = RowCollector(['name','symbol', 'SI', 'CGS', 'AU'], [
('AbsorbedDose',          'ADO',   'Gy',       None,       None),
('Acceleration',          'ACC',   'm/s2',     'cm/s2',    None),
('Action',                'ACT',   'J*s',      None,       '1.054571817e-34*J*s'),
('AmountOfSubstance',     'AOS',   'mol',      None,       None),
('AngularFrequency',      'AFR',   'rad/s',    None,       None),
('Capacitance',           'CAP',   'F',        None,       None),
('CatalyticActivity',     'CAC',   'kat',      None,       None),
('Conductance',           'CON',   'S',        None,       None),
('DynamicViscosity',      'DVI',   'Pa*s',     'g/(cm*s)', None),
('ElectricCurrent',       'ECU',   'A',        None,       '6.623618237510e-3*A'),
('ElectricCharge',        'ECH',   'C',        None,       '1.602176634e-19*C'),
('ElectricChargeDensity', 'ECD',   'C/m3',     None,       '1.08120238457e12*C/m3'),
('ElectricPotential',     'EPO',   'V',        None,       '27.211386245988*V'),
('ElectricDipoleMoment',  'EDM',   'C*m',      'D',        '8.4783536255e-30*C*m'),
('ElectricField',         'EFI',   'V/m',      None,       '5.14220674763e11*V/m'),
('ElectricFieldGradient', 'EFG',   None,       None,       '9.7173624292e21*V/m2'),
('ElectricPolarizability','EPL',   None,       None,       '1.64877727436e-41*C2*m2/J'),
('ElectromotiveForce',    'EFO',   'V',        None,       None),
('Energy',                'ENE',   'J',        'erg',      '4.3597447222071e-18*J'),
('EquivalentDose',        'EDO',   'Sv',       None,       None),
('Force',                 'FOR',   'N',        'dyn',      '8.2387234983e-8*N'),
('Frequency',             'FRE',   'Hz',       None,       None),
('Heat',                  'HEA',   'J',        None,       None),
('Illuminance',           'ILL',   'lx',       None,       None),
('Impedance',             'IMP',   'Ohm',      None,       None),
('Inductance',            'IND',   'H',        None,       None),
('Irradience',            'IRR',   'W/m2',     None,       '6.4364099007e19*W/m2'),
('KinematicViscosity',    'KVI',   'm2/s',     'cm2/s',    None),
('Length',                'LEN',   'm',        'cm',       '5.29177210903e-11*m'),
('LuminousIntensity',     'LIN',   'cd',       None,       None),
('LuminousFlux',          'LFL',   'lm',       None,       None),
('MagneticFlux',          'MFL',   'Wb',       None,       None),
('MagneticFluxDensity',   'MFD',   'T',        'G',        '2.35051756758e5*T'),
('MagneticDipoleMoment',  'MDM',   None,       None,       '1.85480201566e-23*J/T'),
('Magnetizability',       'MAG',   None,       None,       '7.8910366008e-29*J/T2'),
('Mass',                  'MAS',   'kg',       'g',        '9.1093837015e-31*kg'),
('Momentum',              'MOM',   None,       None,       '1.99285191410e-24*kg*m/s'),
('Permittivity',          'PER',   None,       None,       '1.11265005545e-10*F/m'),
('PlaneAngle',            'PAN',   'rad',      None,       None),
('Power',                 'POW',   'W',        'erg/s',    None),
('Pressure',              'PRE',   'Pa',       'Ba',       '2.9421015697e13*Pa'),
('RadiantFlux',           'RFL',   'W',        None,       None),
('Radioactivity',         'RAD',   'Bq',       None,       None),
('Reactance',             'REA',   'Ohm',      None,       None),
('Resistance',            'RES',   'Ohm',      None,       None),
('SolidAnge',             'SAN',   'sr',       None,       None),
('Stress',                'STR',   'Pa',       None,       None),
('Temperature',           'TEM',   'K',        None,       None),
('Time',                  'TIM',   's',        's',        '2.4188843265857e-17*s'),
('Velocity',              'VEL',   'm/s',      'cm/s',     '2.18769126364e6*m/s'),
('Voltage',               'VOL',   'V',        None,       None),
('Wavenumber',            'WAV',   'm-1',      'cm-1',     None),
('Weight',                'WEI',   'N',        None,       None),
('Work',                  'WOR',   'J',        None,       None),
])
SI  = Enum('SI', dict(zip(QUANTITY_LIST.name, [f"#S{symbol}" for symbol in QUANTITY_LIST.symbol])))
CGS = Enum('SI', dict(zip(QUANTITY_LIST.name, [f"#C{symbol}" for symbol in QUANTITY_LIST.symbol])))
AU  = Enum('SI', dict(zip(QUANTITY_LIST.name, [f"#A{symbol}" for symbol in QUANTITY_LIST.symbol])))