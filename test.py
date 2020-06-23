import pickle
from src.core_loop_lem import core_loop_lem
from src.create_players import create_players
from src.core_loop_coop import core_payments, core_loop_coop
import time
import sys
import os 

os.environ["TMP"] = os.path.expanduser('~/tmp/')

if __name__ == '__main__':

    N, H, D, seed, flat, firstday, forcast_type, cant_bats, text = sys.argv[1:]
    N, H, D, seed, firstday, flat, forcast_type, cant_bats = int(N), int(H), int(D), int(seed), int(firstday), int(flat), int(forcast_type), int(cant_bats)
    flat = bool(flat)




    start = time.perf_counter()

    #simpath = create_players(50, 48, 5, 1234, True, 150, '4')
    simpath = create_players(N, H, D, seed, flat, firstday, forcast_type, cant_bats, text)
    simpath += '/'


    ### Cooperative with rolling horizon
    with open(simpath + 'players.pkl', 'rb') as fh: players = pickle.load(fh)
    with open(simpath + 'sim_config.pkl', 'rb') as fh: config = pickle.load(fh)

    res = core_loop_coop(players, config, simpath)


    ## Core payments with perfect information
    with open(simpath + 'players.pkl', 'rb') as fh: players = pickle.load(fh)
    with open(simpath + 'sim_config.pkl', 'rb') as fh: config = pickle.load(fh)

    core_payments(players, config, simpath)

    ### Market simulation with MUDA

    with open(simpath + 'players.pkl', 'rb') as fh: players = pickle.load(fh)
    with open(simpath + 'sim_config.pkl', 'rb') as fh: config = pickle.load(fh)

    core_loop_lem(players, config, simpath, 'muda')

    ### Market simulation with P2P

    with open(simpath + 'players.pkl', 'rb') as fh: players = pickle.load(fh)
    with open(simpath + 'sim_config.pkl', 'rb') as fh: config = pickle.load(fh)

    core_loop_lem(players, config, simpath, 'p2p')

    ### Simulation without market

    with open(simpath + 'players.pkl', 'rb') as fh: players = pickle.load(fh)
    with open(simpath + 'sim_config.pkl', 'rb') as fh: config = pickle.load(fh)

    config['MARKET'] = False
    core_loop_lem(players, config, simpath, 'nomarket')


    ### The END

    elapsed = time.perf_counter() - start
    print('Elapsed time', elapsed)
