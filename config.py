import os
from os.path import expanduser

home = expanduser("~")
SIMULATION_PARAMETERS = home + '/Simulations/journallem'

if not os.path.isdir(SIMULATION_PARAMETERS):
    os.makedirs(SIMULATION_PARAMETERS)


DATAPATH = home + '/github/lem_journal_code/load_profiles/'

DATA = DATAPATH + 'home_data_2012-13.csv'
DATA_SOLAR = DATAPATH + 'home_data_2012-13_rand_03.csv'
DATA_FORCAST = DATAPATH + 'home_data_2012-13_forcast.csv'
DATA_SOLAR_FORCAST = DATAPATH + 'home_data_2012-13_rand_03_forcast.csv'

CPLEX_PATH = "/home/guso/.local/bin/ibm/cplex/bin/x86-64_linux/cplex"


