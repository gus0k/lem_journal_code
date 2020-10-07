# Simulations for comparing individuals to communities

## Running

Parameters for the run function:

* N: number of players to use. 
* H: number of time-slots to look forward
* D: number of days to simulate into the future
* seed: random integer
* flat: True if flat tariff, false if not
* firstday: offset in the numbers of day to use, all data => 0
* forcast_type: 0 => use real data, 1 => use forecasts (need to be provided)
* cant_bats: [0, N], number of players with batteries
* text: name of the simulation

## Example

50 players, 30min time-slots, 6 days simulated (7 need to be provided)

```sh
python run.py 50 48 6 2210 1 0 0 25 first_windows
```

Later, to generate the three different cases: no bat, individual, cooperative run

```sh
python src\extract_post_loads.py
```
