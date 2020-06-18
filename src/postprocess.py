import numpy as np
import pickle
from src.core_loop_lem import core_loop
from src.create_players import create_players
from src.core_loop_coop import core_payments, core_loop_coop
import time



simpath = create_players(10, 48, 10, 1234, False, 100)
simpath += '/'

#simpath = '/home/guso/Simulations/journallem/10-48-10-1234-False-100/'

with open(simpath + 'players.pkl', 'rb') as fh: players = pickle.load(fh)
with open(simpath + 'sim_config.pkl', 'rb') as fh: config = pickle.load(fh)
with open(simpath + 'simres.pkl', 'rb') as fh: aftersim = pickle.load(fh)
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
payments_market = np.array([
    aftersim[i]['history_cost'].sum() for i in range(P)
    ])

## Total cost of the players
total_cost_coop = core_payments_mpc.sum()
total_cost_lem  = payments_market.sum()

## Total amount of energy not traded locally
net_load_coop = np.abs(core_loop[1]).sum()

net_load_lem = np.abs(np.vstack([
    aftersim[p]['history_post_net'] for p in range(P)
    ]).sum(axis=0)).sum()
