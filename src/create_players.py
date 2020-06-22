import numpy as np
import pandas as pd
import time
import sys
import pickle
import json
from src.players import get_player_template, random_player
from src.utils import lazy_pickle
from src.process_data import get_data
from itertools import product

#from json_tricks import dump, dumps, load, loads, strip_comments


from config import *

def create_players(N, H, D, seed, flat=False, real_data=-1, forcast_type=0, cant_bats=None, aux=''):
    print(real_data)


    pt = 'solar'
    filename = map(str, [N, H, D, seed, flat, real_data, forcast_type, cant_bats])
    filename = '-'.join(filename) + '_{0}'.format(aux)
    file_path = SIMULATION_PARAMETERS + '/' + filename

    if not os.path.isdir(file_path):
        os.makedirs(file_path)
    else:
        print('Parameters already created')
        return file_path


    r = np.random.RandomState(seed)
    player_ids = r.choice(np.arange(126), N, replace=False)

    data_original = pd.read_csv(DATA, index_col='date', parse_dates=True)
    data_forcast = pd.read_csv(DATA_FORCAST, index_col='date', parse_dates=True)
    dfs_nosolar = [data_original, data_forcast]

    data_solar= pd.read_csv(DATA_SOLAR, index_col='date', parse_dates=True)
    data_solar_forcast = pd.read_csv(DATA_SOLAR_FORCAST, index_col='date', parse_dates=True)
    dfs_solar = [data_solar, data_solar_forcast]


    if cant_bats is None:
        cant_bats = N
    players_with_bats = r.choice(range(N), size=cant_bats, replace=False)

    players = {}
    for n in range(N):
        has_solar = n <= (N // 2)
        DFS = dfs_solar if has_solar else dfs_nosolar
        if real_data > 0:
            load_ = get_data(n, real_data, D, DFS[0])
            forcast_ = get_data(n, real_data, D, DFS[forcast_type])
        else:
            load_ = None
            forcast_ = None
        val = random_player(H, D, pt, r, flat, load=load_, forcast=forcast_, solar=has_solar)
        players[n] = val


    for p in range(N):
        players[p]['freq'] = None # Players won't update their beliefs

    for p in players_with_bats:
        players[p]['bmax'] = 13.5
        players[p]['dmax'] = 1.25
        players[p]['dmin'] = 1.25

    players_path = file_path + '/players.pkl'
    with open(players_path, 'wb') as fh:
        pickle.dump(players, fh)

    config_path = file_path + '/sim_config.pkl'
    DL = 48
    CONFIG = {
            'ROUNDS': DL * D - H + 1,
            'SLICE': H,
            'RANDOM_STATE': r,
            'MARKET': True,
            'ONLYPRICE': False,
            }
    with open(config_path, 'wb') as fh:
        pickle.dump(CONFIG, fh)

    return file_path


