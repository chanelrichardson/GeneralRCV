import json
import sys
import random
import numpy as np
from pathlib import Path
import os

# Currently this script needs to be manually re-parameterized. That's currently the best way to 
# do things unless there is a desire to make a configuration file for this script
# that makes a configuration file. All of the parameters are detailed 
# in ModelConfiguration.py


nested=False
nested_str = ""
loc_add = 0

if len(sys.argv) > 3: 
  if len(sys.argv) == 4 and sys.argv[-1] == "--nested":
    nested=True
    nested_str = "-nested"
    loc_add = -1

mag_list = json.loads(sys.argv[-1+loc_add])
nested_mag = np.nonzero(mag_list)[0][0]+3
location = sys.argv[-2+loc_add]

mag_str = f"{mag_list[0]}-{mag_list[1]}-{mag_list[2]}"

MULTIPLIER = 3
SEATS = int(nested_mag)

neutral_data = tilted_data = []

read = Path(f"output/records/{location}-{mag_str}{nested_str}")
write = Path(f"output/records/{location}-{mag_str}{nested_str}")

with open(read/"neutral.jsonl", "r") as f:
  for line in list(f): 
    neutral_data.append(json.loads(line))

with open(read/"tilted.jsonl", "r") as f: 
  for line in list(f):
    tilted_data.append(json.loads(line))


# Setting concentration scenarios meaning White support for White pref, White support for POC pref...
# Hard-coding for now, but will change if time permits. 
concentrations = [[0.5, 0.5, 0.5, 0.5], 
                  [1, 1, 1, 1], 
                  [0.5, 1, 1, 0.5], 
                  [0.5, 2, 2, 0.5]]

models = ["bradley-terry", "plackett-luce", "crossover", "cambridge"]
c_names = ["A", "B", "C", "D"]

config = {f"{location}": {"neutral": [], "tilted":[]}}

for plan in range(len(neutral_data)):

  config[location]["neutral"].append([])
  config[location]["tilted"].append([])  

  for district in list(neutral_data[plan].keys()):

    config[location]["neutral"][plan].append([])
    config[location]["tilted"][plan].append([]) 
    pocshare = neutral_data[plan][district]["POCVAP20%"]

    for model in models:

      for c_name, concentration in zip(c_names, concentrations):
           
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
      config[location]["tilted"][plan][int(district)-1].append(config_dict)

write = Path(f"configurations/{location}/racial-basic")
os.makedirs(write, exist_ok = True)

with open(write/f"config-{mag_list[0]}-{mag_list[1]}-{mag_list[2]}{nested_str}.json", "w+") as f:
  json.dump(config, f)

