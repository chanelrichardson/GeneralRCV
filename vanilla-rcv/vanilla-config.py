import json
import sys
import random
import numpy as np
from pathlib import Path
import os


districts = sys.argv[-1]
location = sys.argv[-2]

MULTIPLIER = 3
SEATS = 1

neutral_data = tilted_data = []

read = Path(f"output/records/{location}-{districts}-vanilla")
#write = Path(f"output/records/{location}-{mag_list[0]}-{mag_list[1]}-{mag_list[2]}{nested_str}")

with open(read/"neutral.jsonl", "r") as f:
  for line in list(f): 
    neutral_data.append(json.loads(line))

"""
with open(write/"tilted.jsonl", "r") as f: 
  for line in list(f):
    tilted_data.append(json.loads(line))
"""

# Setting concentration scenarios meaning White support for White pref, White support for POC pref...
# Hard-coding for now, but will change if time permits. 
concentrations = [[0.5, 0.5, 0.5, 0.5], 
                  [1, 1, 1, 1], 
                  [0.5, 1, 1, 0.5], 
                  [0.5, 2, 2, 0.5]]

models = ["bradley-terry", "plackett-luce", "crossover", "cambridge"]
c_names = ["A", "B", "C", "D"]

config = {f"{location}": {"neutral": []}}

for plan in range(len(neutral_data)):

  config[location]["neutral"].append([])
  #config[location]["tilted"].append([])  
  config[location]["neutral"][plan] = [[] for i in range(len(neutral_data[plan].keys()))]
  for ix, district in enumerate(list(neutral_data[plan].keys())):

    #config[location]["neutral"][plan].append([])
    #config[location]["tilted"][plan].append([]) 
    pocshare = neutral_data[plan][district]["POCVAP20%"]

    for model in models:

      for c_name, concentration in zip(c_names, concentrations):
          """ 
          if pocshare > 0.4: 
            if SEATS*MULTIPLIER == 12:
              wcand = 4
              ccand = 8
            else: 
              wcand = 3
              ccand = 7
          elif 0.25 <= pocshare <= 0.4: 
            if SEATS*MULTIPLIER == 12: 
              wcand = ccand = 6
            else:
              wcand = ccand = 5
          else:
            if SEATS*MULIPLIER == 12:
              wcand = 9
              ccand = 3
            else: 
              wcand = 8
              ccand = 2
          """
          config_dict = {"pp": 0.8, 
                 "pw": 0.2, 
                 "ww": 0.7,
                 "wp": 0.3,
                 "pocshare": pocshare,
                 "seats":  SEATS, 
                 "multiplier":MULTIPLIER,
                 "poc": pocshare, 
                 "ballots": 1000, 
                 "simulations": 100, 
                 "model": model, 
                 "concentration": concentration, 
                 "concentrationname": c_name, 
                 "candidates": SEATS*MULTIPLIER, 
                 "poccandidates": round(SEATS*MULTIPLIER*pocshare), 
                 "wcandidates": round(SEATS*MULTIPLIER*(1-pocshare))}

      #add this new configuration to all our list of configurations
      config[location]["neutral"][plan][int(district)-1].append(config_dict)
      #config[location]["tilted"][plan][int(district)-1].append(config_dict)

write = Path(f"configurations/{location}/racial-basic")
os.makedirs(write, exist_ok = True)

with open(write/f"config-{districts}-vanilla.json", "w+") as f:
  json.dump(config, f)

