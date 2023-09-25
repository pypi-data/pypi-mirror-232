from importlib.metadata import version

__version__ = version ('loupiotes')

import loupiotes.tables

import loupiotes.spots

from .intensity import *

from .solar_coordinates import *

global Rsun
global Msun
global Gravity_constant
global sun_mean_synodic_period

Rsun = 6.96e8
Msun = 1.9847e30
Gravity_constant = 6.6743e-11
sun_mean_synodic_period = 27.275261151446653

