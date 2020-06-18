import pickle
from src.core_loop_lem import core_loop
from src.create_players import create_players
from src.core_loop_coop import core_payments, core_loop_coop
import time


start = time.perf_counter()

simpath = create_players(10, 48, 10, 1234, False, 100)
simpath += '/'

#simpath = '/home/guso/Simulations/journallem/10-48-10-1234-False-100/'

with open(simpath + 'players.pkl', 'rb') as fh: players = pickle.load(fh)
with open(simpath + 'sim_config.pkl', 'rb') as fh: config = pickle.load(fh)

res = core_loop(players, config, simpath)

with open(simpath + 'players.pkl', 'rb') as fh: players = pickle.load(fh)
with open(simpath + 'sim_config.pkl', 'rb') as fh: config = pickle.load(fh)

core_loop = core_loop_coop(players, config, simpath)

with open(simpath + 'players.pkl', 'rb') as fh: players = pickle.load(fh)
with open(simpath + 'sim_config.pkl', 'rb') as fh: config = pickle.load(fh)

core_payoffs = core_payments(players, config, simpath)

elapsed = time.perf_counter() - start
print('Elapsed time', elapsed)
