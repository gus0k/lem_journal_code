import pickle
import numpy as np
from config import SIMULATION_PARAMETERS, TIMESLOTS_HOUR
from pathlib import Path


sim_spec = '50-48-6-2210-True-0-0-25_first_windows'
simpath = Path(SIMULATION_PARAMETERS) / sim_spec
OUT = Path('~/Simulations').expanduser()


with open(simpath / 'players.pkl', 'rb') as fh: players = pickle.load(fh)
with open(simpath / 'sim_config.pkl', 'rb') as fh: config = pickle.load(fh)
with open(simpath / 'nomarket.pkl', 'rb') as fh: nomarket = pickle.load(fh)
with open(simpath / 'coop_loop_res.pkl', 'rb') as fh: core_loop = pickle.load(fh)


CHARGE_COEF = 0.8
ROUNDS = config['ROUNDS']

### Net load players cooperating

coop_cost = core_loop[0].sum()

players = core_loop[2].keys()

net_coop = []
charge_coop = 0
for pl in players:
    clp = core_loop[2][pl]
    ec, ed = clp['efc'], clp['efd']
    bat    = np.array([
        x / ec if x >=0 else x * ed for x in clp['history_bat']])
    net = bat + clp['allload']
    charge_coop += clp['charge']
    net_coop.append(net)

charge_coop *= CHARGE_COEF

net_coop = np.vstack(net_coop)

ps = core_loop[2][0]['allprices'][:, 0]
pb = core_loop[2][0]['allprices'][:, 3]

cost_coop = sum([n * pb_ if n >= 0 else n * ps_ for n, pb_, ps_ in
        zip(net_coop.sum(axis=0)[:ROUNDS], pb, ps)]) - charge_coop * pb[0]
cost_coop2 = sum([n * pb_ if n >= 0 else n * ps_ for n, pb_, ps_ in
        zip(core_loop[1][:ROUNDS], pb, ps)]) - charge_coop * pb[0]

net_coop *= TIMESLOTS_HOUR # from kWh to kW


#### Net loads individually

net_indiv = []
charge_indiv = 0
for pl in players:
    net = nomarket[pl]['history_post_net'][:ROUNDS]
    charge_indiv += nomarket[pl]['charge']
    net_indiv.append(net)

charge_indiv *= CHARGE_COEF

net_indiv = np.vstack(net_indiv)

ps = nomarket[0]['allprices'][:, 0]
pb = nomarket[0]['allprices'][:, 3]

cost_indiv = sum([n * pb_ if n >= 0 else n * ps_ for n, pb_, ps_ in
        zip(net_indiv.sum(axis=0)[:ROUNDS], pb, ps)]) - charge_indiv * pb[0]

net_indiv *= TIMESLOTS_HOUR # To kW

#### Only loads

net_nobat = []
for pl in players:
    net = nomarket[pl]['allload'][:ROUNDS]
    net_nobat.append(net)

net_nobat = np.vstack(net_nobat)

cost_nobat = sum([n * pb_ if n >= 0 else n * ps_ for n, pb_, ps_ in
        zip(net_nobat.sum(axis=0)[:ROUNDS], pb, ps)])

net_nobat *= TIMESLOTS_HOUR # kwh To kW

print(cost_nobat)
print(cost_indiv)
print(cost_coop)


##### Saving results



np.savetxt(OUT / 'nobat.csv', net_nobat, delimiter=',')
np.savetxt(OUT / 'indiv.csv', net_indiv, delimiter=',')
np.savetxt(OUT / 'coop.csv', net_coop,  delimiter=',')

