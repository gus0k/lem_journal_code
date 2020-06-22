import numpy as np

MAX = 20
SEED = 22101994
reps=2

randomstate = np.random.RandomState(SEED)

N = '50'
H = '48'
D = '5'

name = 'complete'

FD = np.arange(1, 150, 6)
FDL = FD.shape[0]

for N in ['20', '50', '70']:
    for cb in [1, 2, 4]:
        cantbats = str(int(N) // cb)
        for fd in FD:
            for seed in randomstate.randint(1, 100000, reps):
                for flat in ['0', '1']:
                    for forcast in ['0', '1']:
                        string = ' '.join([N, H, D])
                        string += ' ' + str(seed)
                        string += ' ' + flat
                        string += ' ' + str(fd)
                        string += ' ' + forcast
                        string += ' ' + cantbats
                        string += ' ' + name
                        print(string)



        


