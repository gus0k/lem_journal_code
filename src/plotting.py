import numpy as np
import pickle
import matplotlib.pyplot as plt
from src.create_players import create_players
import time
from config import *

from pathlib import Path
from src.utils import fix_hist_step_vertical_line_at_end

import matplotlib
#matplotlib.use('pgf'),
# matplotlib.rcParams.update({
    # 'pgf.texsystem': 'pdflatex',
    # 'font.family': 'serif',
    # 'text.usetex': True,
    # 'pgf.rcfonts': False,
# }),

def process_sim(simpath):

    params = simpath.split('/')[-2]
    params, name = params.split('_')
    params = params.split('-')
    if len(params) != 7:
        return None
    N, H, D, seed, flat, fd, forcast = params

    with open(simpath + 'players.pkl', 'rb') as fh: players = pickle.load(fh)
    with open(simpath + 'sim_config.pkl', 'rb') as fh: config = pickle.load(fh)
    with open(simpath + 'simres_muda.pkl', 'rb') as fh: aftersim_muda = pickle.load(fh)
    with open(simpath + 'simres_p2p.pkl', 'rb') as fh: aftersim_p2p = pickle.load(fh)
    with open(simpath + 'nomarket.pkl', 'rb') as fh: nomarket = pickle.load(fh)
    with open(simpath + 'coop_loop_res.pkl', 'rb') as fh: core_loop = pickle.load(fh)
    with open(simpath + 'core_payments.pkl', 'rb') as fh: core_payoffs = pickle.load(fh)

    P = int(N)
    lemsims = [aftersim_muda, aftersim_p2p, nomarket]

    ## Charges
    PERC = 0.95
    PLS = [core_loop[2], aftersim_muda, aftersim_p2p, nomarket]
    charges = [sum([pls_[n]['charge'] for n in range(P)]) for pls_ in PLS]

    ## Net load
    net_load_coop = np.abs(core_loop[1]).sum() - charges[0] * PERC
    net_load_coop_perf = np.abs(core_payoffs[1]).sum()

    netloads_lemsims = []
    for i, sim in enumerate(lemsims):
        net = np.abs(np.vstack([sim[p]['history_post_net'] for p in range(P) ]).sum(axis=0)).sum()
        net -= charges[i + 1] * PERC
        netloads_lemsims.append(net)

    ## Costs
    payments_lemsims = []
    for i, sim in enumerate(lemsims):
        payments = np.array([sim[i]['history_cost'].sum() for i in range(P)]).sum()
        payments -= charges[i + 1] * PERC * 10 # FiT = 10
        payments_lemsims.append(payments)

    total_cost_coop = core_loop[0].sum() - charges[0] * PERC * 10 # FiT = 10
    total_cost_perf = core_payoffs[0].sum()

    if total_cost_perf > payments_lemsims[1]:
        print(simpath) 
        print(total_cost_perf)
        print(payments_lemsims[1])


    results = {
            'netload': {
                'perf': net_load_coop_perf,
                'coop': net_load_coop,
                'muda': netloads_lemsims[0],
                'p2p' : netloads_lemsims[1],
                'nomr': netloads_lemsims[2],
                },
            'cost': {
                'perf': total_cost_perf,
                'coop': total_cost_coop,
                'muda': payments_lemsims[0],
                'p2p' : payments_lemsims[1],
                'nomr': payments_lemsims[2],
                }
            }
    return results, params



def generate_figures(sims, flat='True', forcast='0'):

    data_cost = [[], [], [], []]
    data_load = [[], [], [], []]
    data = [data_cost, data_load]
    data_keys = ['cost', 'netload']

    KEYS_SIMNAMES = ['perf', 'coop', 'muda', 'p2p']
    KEYS_SIM_LONG = ['Cooperative perfect', 'Cooperative iterative', 'Non-coop MUDA', 'Non-coop P2P ']

    for ss in sims:
        X = process_sim(ss)
        if X is not None:
            res, par = X
            if (par[4], par[6]) == (flat, forcast):

                for i, d_ in enumerate(data):
                    tmp = res[data_keys[i]]
                    for j, key in enumerate(KEYS_SIMNAMES):
                        val = round(tmp[key] / tmp['nomr'] * 100, 1)
                        d_[j].append(val)


    flat_title = ' - Flat tariff - ' if flat == 'True' else ' - Tou Tariff - '
    forcast_title = ' - No forcast - ' if forcast == '0' else ' - with forcast - '


    BINS = 20
    FIGSIZE = (12, 10)
    fig_cost, ax = plt.subplots(figsize=FIGSIZE)
    

    for i, d_ in enumerate(data_cost):
        label = KEYS_SIM_LONG[i]
        ax.hist(d_, BINS, density=True, histtype='step', cumulative=True, label=label)

    fix_hist_step_vertical_line_at_end(ax)
    ax.legend()
    ax.set_xlabel('% smaller than to no interaction')
    ax.set_ylabel('Fraction of simulations')
    ax.set_title('Cost' + flat_title + forcast_title)
    ax.legend()
    fig_cost.tight_layout()


    fig_load, ax = plt.subplots(figsize=FIGSIZE)

    for i, d_ in enumerate(data_load):
        label = KEYS_SIM_LONG[i]
        ax.hist(d_, BINS, density=True, histtype='step', cumulative=True, label=label)

    fix_hist_step_vertical_line_at_end(ax)
    ax.set_xlabel('% smaller than to no interaction')
    ax.set_ylabel('Fraction of simulations')
    ax.set_title('Energy exchanged with the grid' + flat_title + forcast_title)
    ax.legend()
    fig_load.tight_layout()

    return fig_load, fig_cost
           

if __name__ == '__main__':
    sims = [str(s) + '/' for s in Path(SIMULATION_PARAMETERS).glob('*good1')]

    combs = [('True', '0'), ('True', '1'), ('False', '0'), ('False', '1')]
    for flat, forcast in combs:
        fl, fc = generate_figures(sims, flat, forcast)
        fl.savefig('img/fl{}{}.png'.format(flat, forcast))
        fc.savefig('img/fc{}{}.png'.format(flat, forcast))

