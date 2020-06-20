import numpy as np

MAX = 20
SEED = 22101994
reps=2

randomstate = np.random.RandomState(SEED)

N = '50'
H = '48'
D = '5'

name = 'good1'

FD = np.arange(1, 150, 6)
FDL = FD.shape[0]

for fd in FD:
    for seed in randomstate.randint(1, 100000, reps):
        for flat in ['0', '1']:
            for forcast in ['0', '1']:
                string = ' '.join([N, H, D])
                string += ' ' + str(seed)
                string += ' ' + flat
                string += ' ' + str(fd)
                string += ' ' + forcast
                string += ' ' + name
                print(string)



        


