import numpy as np
import pickle
import matplotlib.pyplot as plt
# from src.core_loop_lem import core_loop
from src.create_players import create_players
# from src.core_loop_coop import core_payments, core_loop_coop
import time
from config import *

from pathlib import Path

sims = [str(s) + '/' for s in SIMULATION_PARAMETERS.glob('*')]
for x in enumerate(sims): print(x)

if __name__ == '__main__':

    import sys
    S = sys.argv[1]
    S = int(S)

    simpath = sims[S]
    #simpath = create_players(40, 48, 5, 1234, True, 150, '3')
    #simpath += '/'

    def req_load(pl, config):

        P = len(pl)
        R = config.get('ROUNDS')
        load = np.vstack([pl[i]['allload'][:R] for i in range(P)])
        agg = load.sum(axis=0)
        stored = 0
        total = 0
        prev = 0
        low = True
        for t, ag in enumerate(agg):
            if t % 48 == 32:
                print('Low', total, total - prev, stored)
                prev = total
            if t % 48 == 0:
                print('High', total, total - prev, stored)
                prev = total
            if ag >= 0:
                m = min(ag, stored)
                total += (ag - m)
                stored -= m
            else:
                stored -= ag
        return load, total,stored


    def re_load(pl, config):

        P = len(pl)
        R = config.get('ROUNDS')
        load = np.vstack([pl[i]['allload'][:R] for i in range(P)]).sum(axis=0)
        return load

    def re_net(pl, config):

        P = len(pl)
        R = config.get('ROUNDS')
        load = np.vstack([pl[i]['history_post_net'][:R] for i in range(P)]).sum(axis=0)
        return load



    #simpath = '/home/guso/Simulations/journallem/10-48-10-1234-False-100/'

    with open(simpath + 'players.pkl', 'rb') as fh: players = pickle.load(fh)
    with open(simpath + 'sim_config.pkl', 'rb') as fh: config = pickle.load(fh)
    with open(simpath + 'simres_muda.pkl', 'rb') as fh: aftersim_muda = pickle.load(fh)
    with open(simpath + 'simres_p2p.pkl', 'rb') as fh: aftersim_p2p = pickle.load(fh)
    with open(simpath + 'nomarket.pkl', 'rb') as fh: nomarket = pickle.load(fh)
    with open(simpath + 'coop_loop_res.pkl', 'rb') as fh: core_loop = pickle.load(fh)
    with open(simpath + 'core_payments.pkl', 'rb') as fh: core_payoffs = pickle.load(fh)


    P = len(players)

    # Ratio between perfect info and forecast
    sum_cost_perfect_coop = core_payoffs[0].sum()
    sum_cost_imperfect_coop = core_loop[0].sum()
    ratio_mpc = sum_cost_imperfect_coop / sum_cost_perfect_coop

    # Cost per player when implementing coop game
    core_payments_mpc = core_payoffs[0] * ratio_mpc

    ## Cost per player when trading in the market
    payments_market_muda = np.array([
        aftersim_muda[i]['history_cost'].sum() for i in range(P)
        ])

    payments_market_p2p = np.array([
        aftersim_p2p[i]['history_cost'].sum() for i in range(P)
        ])

    payments_nomarket = np.array([
        nomarket[i]['history_cost'].sum() for i in range(P)
        ])

    ## Total cost of the players
    total_cost_coop = core_payments_mpc.sum()
    total_cost_lem_muda  = payments_market_muda.sum()
    total_cost_lem_p2p  = payments_market_p2p.sum()
    total_cost_nomarket  = payments_nomarket.sum()


    ## Total amount of energy not traded locally
    net_load_coop = np.abs(core_loop[1]).sum()

    net_load_lem_muda = np.abs(np.vstack([ aftersim_muda[p]['history_post_net'] for p in range(P) ]).sum(axis=0)).sum()

    net_load_lem_p2p = np.abs(np.vstack([ aftersim_p2p[p]['history_post_net'] for p in range(P) ]).sum(axis=0)).sum()

    net_load_nomarket = np.abs(np.vstack([ nomarket[p]['history_post_net'] for p in range(P) ]).sum(axis=0)).sum()

    ## Stored energy

    PLS = [core_loop[2], aftersim_muda, aftersim_p2p, nomarket]
    charges = [sum([pls_[n]['charge'] for n in range(P)]) for pls_ in PLS]

    PERC = 0.9


    print('Cost Perf      ', round(core_payoffs[0].sum()))
    print('Cost Coop      ', round(total_cost_coop - charges[0] * PERC * 10 ))
    print('Cost MUDA      ', round(total_cost_lem_muda - charges[1] * PERC * 10  ))
    print('Cost p2p       ', round(total_cost_lem_p2p - charges[2] * PERC * 10 ))
    print('Cost No market ', round( total_cost_nomarket - charges[3] * PERC * 10  ))

    print('-' * 20)

    print('Net load perf      ', round(np.abs(core_payoffs[1]).sum()))
    print('Net load Coop      ', round(net_load_coop - charges[0] * PERC))
    print('Net load MUDA      ', round(net_load_lem_muda - charges[1] * PERC))
    print('Net load p2p       ', round(net_load_lem_p2p - charges[2] * PERC))
    print('Net load No market ', round(net_load_nomarket - charges[3] * PERC))

