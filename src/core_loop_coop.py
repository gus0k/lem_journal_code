from src.structure import init_problem, update_problem, cleanup_solution
from collections import deque
from src.priors import *
from src.market import MarketInterface, prepare_bid
import numpy as np
import os
import pickle
from src.player_coop import Player
from src.coop_model import solve_centralized, extract_core_payment


def init_players(players):
    P = len(players)
    L = players[0]['L']
    for i in range(P):
        data = players[i]
        mo, c_, v_ = init_problem(data)
        players[i]['model'] = mo
        players[i]['con'] = c_
        players[i]['var'] = v_
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

    player_list = []

    for p in range(P):
        pl = players[p]
        x   = pl['allload'][ : ROUNDS ]
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

    with open(res_path, 'wb') as fh:
        for k, pl in players.items(): # Model can't be pickled
            pl.pop('model', None)
            pl.pop('con', None)
            pl.pop('var', None)

        pickle.dump([payoff, player_list], fh)

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
            x   = pl['allforcast'][i : i + SLICE]
            x[0] = pl['allload'][i]
            sm  = pl['bmax']
            s0  = pl['charge']
            ram = pl['dmax']
            ec  = pl['efc']
            ed  = pl['efd']
            p_ = Player(x, sm, s0, ram, ec, ed)
            player_list.append(p_)

        price_buy = pl['allprices'][ i : i + SLICE, 3]
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
        c = price_buy[0] * res[1][0][0].varValue
        c -= price_sell[0] * res[1][1][0].varValue
        net_load[i] = net
        cost[i] = c

    with open(res_path, 'wb') as fh:
        for k, pl in players.items(): # Model can't be pickled
            pl.pop('model', None)
            pl.pop('con', None)
            pl.pop('var', None)

        pickle.dump([cost, net_load, players], fh)

    return None





def core_loop_(players, config, simpath):
    
    res_path = simpath + 'simres.pkl'
    if os.path.exists(res_path):
        print('Simulation result already exists')
        return None

    ROUNDS = config['ROUNDS']
    SLICE = config['SLICE']
    r = config['RANDOM_STATE']
    P = len(players)
    MARKET = config.get('MARKET', True)
    ONLYPRICE = config.get('ONLYPRICE', False)

    init_players(players)

    for i in range(ROUNDS):

        for p in range(P):

            data = players[p]
            mo, c_, v_ = data['model'], data['con'], data['var']
            data['price'] = data['allprices'][i: i + SLICE, :]
            data['load'] = data['allforcast'][i : i + SLICE]
            data['load'][0] = data['allload'][i]


            if MARKET:
                mo = update_problem(mo, c_, v_, data)
                _ = mo.solve()
                sol = cleanup_solution(mo, c_, v_, data)

                bat = sol['var'][SLICE] - sol['var'][2 * SLICE]
                net = sol['net'][0]
                data['history_pre_net'][i] = net

                price = data['price'][0, :]
                bids = prepare_bid(p, net, price)
                if bids is not None:
                    for bi in bids:
                        id_bid = mar.accept_bid(bi)


        if MARKET:
            mar.clear()
        for p in range(P):

            data = players[p]
            data['commitment'] = None
            mo, c_, v_ = data['model'], data['con'], data['var']

            if MARKET:
                if p in mar.users_to_key:
                    mtq, mtp = mar.get_user_result(p)
                    set_prior_with_market(data, mtq, mtp)
                    accumulate_sample(i, data, mtq, mtp)

                    if not np.allclose(mtq, 0):
                        data['commitment'] = mtq

            
            mo = update_problem(mo, c_, v_, data)
            _ = mo.solve()
            sol = cleanup_solution(mo, c_, v_, data)

            bat = sol['var'][SLICE] - sol['var'][2 * SLICE]
            net = sol['net'][0]
            data['history_bat'][i] = bat
            data['history_cost'][i] = sol['var'][0]
            data['history_post_net'][i] = sol['net'][0]

            data['charge'] += bat
            data['commitment'] = None
            update_current_prior(i, data, onlyprice=ONLYPRICE)


    with open(res_path, 'wb') as fh:
        for k, pl in players.items(): # Model can't be pickled
            pl.pop('model', None)
            pl.pop('con', None)
            pl.pop('var', None)

        pickle.dump(players, fh)

    return None

