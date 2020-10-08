import os
from pathlib import Path

SIMULATION_PARAMETERS = Path('~/Simulations/lec').expanduser()

if not os.path.isdir(SIMULATION_PARAMETERS):
    os.makedirs(SIMULATION_PARAMETERS)


DATAPATH = Path('~/Projects/sonnen/data').expanduser()
DATA = str(DATAPATH / 'sonnen_m_2020-01-01-2020-01-07.csv')
DATA_SOLAR = str(DATA)
DATA_FORCAST = str(DATA)
DATA_SOLAR_FORCAST = str(DATA)

CPLEX_PATH = 'C:/Program Files/IBM/ILOG/CPLEX_Studio1210/cplex/bin/x64_win64/cplex.exe'

BATTERY_CAPACITY = 13.5
RAMP_UP = 5.
RAMP_DOWN = 5.

TIMESLOTS_HOUR = 2
DL = TIMESLOTS_HOUR * 24
