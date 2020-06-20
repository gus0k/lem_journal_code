from src.structure import init_problem, update_problem, cleanup_solution
from collections import deque
from src.priors import *
import numpy as np
import os
import pickle
from src.player_coop import Player
from src.coop_model import solve_centralized, extract_core_payment


def init_players(players):
    P = len(players)
    L = players[0]['L']
    for i in range(P):
        players[i]['history_bat'] = np.zeros(L)
        players[i]['history_cost'] = np.zeros(L)
        players[i]['history_pre_net'] = np.zeros(L)
        players[i]['history_post_net'] = np.zeros(L)


def core_payments(players, config, simpath):

    res_path = simpath + 'core_payments.pkl'
    if os.path.exists(res_path):
        print('Simulation result already exists')
        return None
    
    P = len(players)
    ROUNDS = config['ROUNDS']
    SLICE = config['SLICE']
    init_players(players)

    net_load = np.zeros(ROUNDS)

    player_list = []

    for p in range(P):
        pl = players[p]
        x   = pl['allload'][ : ROUNDS ].copy()
        sm  = pl['bmax']
        s0  = pl['charge']
        ram = pl['dmax']
        ec  = pl['efc']
        ed  = pl['efd']
        p_ = Player(x, sm, s0, ram, ec, ed)
        player_list.append(p_)
    
    price_buy  = pl['allprices'][: ROUNDS, 3]
    price_sell = pl['allprices'][: ROUNDS, 0]

    res = solve_centralized(player_list, price_buy, price_sell)
    m = res[0]
    payoff = extract_core_payment(player_list, price_buy, price_sell, m)

    for r in range(ROUNDS):
        net = res[1][0][r].varValue - res[1][1][r].varValue
        net_load[r] = net


    with open(res_path, 'wb') as fh:
        for k, pl in players.items(): # Model can't be pickled
            pl.pop('model', None)
            pl.pop('con', None)
            pl.pop('var', None)

        pickle.dump([payoff, net_load], fh)

    return None



def core_loop_coop(players, config, simpath):

    res_path = simpath + 'coop_loop_res.pkl'
    if os.path.exists(res_path):
        print('Simulation result already exists')
        return None

    ROUNDS = config['ROUNDS']
    SLICE = config['SLICE']
    r = config['RANDOM_STATE']
    P = len(players)

    init_players(players)
    net_load = np.zeros(ROUNDS)
    cost = np.zeros(ROUNDS)

    for i in range(ROUNDS):

        player_list = []
        for p in range(P):

            pl = players[p]
            x    = pl['allforcast'][i : i + SLICE].copy()
            x[0] = pl['allload'][i]
            sm   = pl['bmax']
            s0   = pl['charge']
            ram  = pl['dmax']
            ec   = pl['efc']
            ed   = pl['efd']
            p_ = Player(x, sm, s0, ram, ec, ed)
            player_list.append(p_)

        price_buy  = pl['allprices'][i : i + SLICE, 3]
        price_sell = pl['allprices'][i : i + SLICE, 0]
        res = solve_centralized(player_list, price_buy, price_sell)
        ch = res[1][2]
        dis = res[1][3]
        for p in range(P):

            pl = players[p]
            bat = ch[(p, 0)].varValue - dis[(p, 0)].varValue

            pl['history_bat'][i] = bat
            pl['charge'] += bat

        net = res[1][0][0].varValue - res[1][1][0].varValue
        c = price_buy[0] * res[1][0][0].varValue - price_sell[0] * res[1][1][0].varValue

        net_load[i] = net
        cost[i] = c

    with open(res_path, 'wb') as fh:
        for k, pl in players.items(): # Model can't be pickled
            pl.pop('model', None)
            pl.pop('con', None)
            pl.pop('var', None)

        pickle.dump([cost, net_load, players], fh)

    return None





