import os
from pathlib import Path

SIMULATION_PARAMETERS = str(Path('~/Simulations/journallem').expanduser())

if not os.path.isdir(SIMULATION_PARAMETERS):
    os.makedirs(SIMULATION_PARAMETERS)


DATAPATH = Path('~/github/sonnen/data').expanduser()

DATA = str(DATAPATH / 'sonnen_m_2020-01-01-2020-01-07.csv')
DATA_SOLAR = str(DATA)
DATA_FORCAST = str(DATA)
DATA_SOLAR_FORCAST = str(DATA)
#DATA = DATAPATH / 'home_data_2012-13.csv'
#DATA_SOLAR = DATAPATH + 'home_data_2012-13_rand_03.csv'
#DATA_FORCAST = DATAPATH + 'home_data_2012-13_forcast.csv'
#DATA_SOLAR_FORCAST = DATAPATH + 'home_data_2012-13_rand_03_forcast.csv'

CPLEX_PATH = "/home/diego/cplex/cplex/bin/x86-64_linux/cplex"


BATTERY_CAPACITY = 13.5
RAMP_UP = 5.
RAMP_DOWN = 5.

TIMESLOTS_HOUR = 2
DL = TIMESLOTS_HOUR * 24
