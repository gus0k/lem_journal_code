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

import json_tricks as jt
#from json_tricks import dump, dumps, load, loads, strip_comments

from config import *

def create_players(N, T, D, seed, flat=False, real_data=-1):

    pt = 'solar'
    filename = map(str, [N, T, D, seed, flat, real_data])
    filename = '-'.join(filename)
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

    players = {}
    for n in range(N):
        has_solar = n <= (N // 2)
        DFS = dfs_solar if has_solar else dfs_nosolar
        if real_data > 0:
            load_ = get_data(n, real_data, D, DFS[0])
            forcast_ = get_data(n, real_data, D, DFS[1])
        else:
            load_ = None
            forcast_ = None
        val = random_player(T, D, pt, r, flat, load=load_, forcast=forcast_, solar=has_solar)
        players[n] = val


    for p in range(N):
        players[p]['freq'] = None # Players won't update their beliefs

    players_path = file_path + '/players.pkl'
    with open(players_path, 'wb') as fh:
        pickle.dump(players, fh)

    config_path = file_path + '/sim_config.pkl'
    CONFIG = {
            'ROUNDS': T * (D - 1) + 1,
            'SLICE': T,
            'RANDOM_STATE': r,
            'MARKET': True,
            'ONLYPRICE': False,
            }
    with open(config_path, 'wb') as fh:
        pickle.dump(CONFIG, fh)

    return file_path



def run(N, T, D, pt, market, freq, seed, onlyprice=False, flat=False, real_data=-1):


    r = np.random.RandomState(seed)
    player_ids = r.choice(np.arange(126), N, replace=False)

    data_original = pd.read_csv(DATA, index_col='date', parse_dates=True)
    data_forcast = pd.read_csv(DATA_FORCAST, index_col='date', parse_dates=True)
    dfs_nosolar = [data_original, data_forcast]

    data_solar= pd.read_csv(DATA_SOLAR, index_col='date', parse_dates=True)
    data_solar_forcast = pd.read_csv(DATA_SOLAR_FORCAST, index_col='date', parse_dates=True)
    dfs_solar = [data_solar, data_solar_forcast]

#    real_data = int(real_data)
#    if real_data > 0:
#        loads = get_data(real_data, D + 1, N, r)
#    else:
#        loads = None

    players = {}
    for n in range(N):
        has_solar = n <= (N // 2)
        DFS = dfs_solar if has_solar else dfs_nosolar
        if real_data > 0:
            load_ = get_data(n, real_data, D, DFS[0])
            forcast_ = get_data(n, real_data, D, DFS[1])
        else:
            load_ = None
            forcast_ = None
        val = random_player(T, D, pt, r, flat, load=load_, forcast=forcast_, solar=has_solar)
        players[n] = val


    for p in range(N):
        players[p]['freq'] = freq

    CONFIG = {
            'ROUNDS': T * (D - 1) + 1,
            'SLICE': T,
            'RANDOM_STATE': r,
            'MARKET': market,
            'ONLYPRICE': onlyprice,
            }

    start = time.perf_counter()
    welfare, traded = core_loop(players, CONFIG)
    end = time.perf_counter() - start

    for k, pl in players.items():
        pl.pop('model', None)
        pl.pop('con', None)
        pl.pop('var', None)

    return (end, players, welfare, traded)


#if __name__ == "__main__":


    # N, T, D, pt, market, fq, seed, up, ftou, day = sys.argv[1:]
    # N = int(N)
    # T = int(T)
    # D = int(D)
    # market = True if market == 'True' else False 
    # seed = int(seed)
    # up = True if up == 'True' else False
    # ftou = True if ftou == 'True' else False 
    # day = int(day)
    # try:
        # fq = int(fq)
    # except ValueError:
        # fq = None
    # args = (N, T, D, pt, market, fq, seed, up, ftou, day)

    # s = PREF + "-".join(map(str,args)) + "?test5"
    # start = time.perf_counter()
    # lazy_pickle(s)(run)(*args)
    # end = time.perf_counter()

    # with open('times.txt', 'a') as fh:
        # text = s + " {0:2f}\n".format(end - start)
        # fh.write(text)

