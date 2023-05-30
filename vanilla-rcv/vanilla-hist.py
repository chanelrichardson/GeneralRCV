import matplotlib.pyplot as plt
import jsonlines
import sys
import json
from gerrychain.updaters import Tally
from gerrychain import Graph, Partition
from gerrytools.scoring import * 
import numpy as np
from gerrytools.plotting import * 
districts = sys.argv[-1]
location = sys.argv[-2]


read = f"output/chains/{location}-{districts}-vanilla"

neutral_plans = []
with open(f"{read}/neutral-assignments.jsonl", "r") as f:
  for line in f:
    my_line = json.loads(line)
    to_append = {}
    for k, v in my_line.items():
      to_append[int(k)] = v
    neutral_plans.append(to_append)

graph = Graph.from_json(f"data/graphs/{location}.json")

updaters = {"POCVAP20": Tally("POCVAP20", "POCVAP20"), 
            "VAP20": Tally("VAP20", "VAP20"), 
            "BHVAP20": Tally("BHVAP20", "BHVAP20"), 
            }
          
all_plan_shares = {"poc_30": [], "poc_40": [], "bh_30": [], "bh_40": []}
for plan in neutral_plans[:100]:
  partition = Partition(graph, plan, updaters = updaters)
  share_scores = demographic_shares({"VAP20": ["POCVAP20", "BHVAP20"]})
  share_dict = summarize(partition, share_scores)
  poc_30 = len([v for v in share_dict["POCVAP20_share"].values() if v > 0.3]) 
  poc_40 = len([v for v in share_dict["POCVAP20_share"].values() if v > 0.4])
  bh_30 = len([v for v in share_dict["BHVAP20_share"].values() if v > 0.3])
  bh_40 = len([v for v in share_dict["BHVAP20_share"].values() if v > 0.4])

  all_plan_shares["poc_30"].append(poc_30)
  all_plan_shares["poc_40"].append(poc_40)
  all_plan_shares["bh_30"].append(bh_30)
  all_plan_shares["bh_40"].append(bh_40)

print(all_plan_shares["poc_30"])
_, ax_poc_30 = plt.subplots(1, 1, figsize=(7.5, 5))
_, ax_poc_40 = plt.subplots(1, 1, figsize=(7.5, 5))
_, ax_bh_30 = plt.subplots(1, 1, figsize=(7.5, 5))
_, ax_bh_40 = plt.subplots(1, 1, figsize=(7.5, 5))

bins = np.linspace(0, 20, 2)
 
ax_poc_30 = histogram(ax_poc_30, {"ensemble":all_plan_shares["poc_30"], "proposed": [], "citizen": []}, label=f"{location} {districts} districts, > 30% POC", fontsize=10)
ax_poc_40 = histogram(ax_poc_40, {"ensemble":all_plan_shares["poc_40"], "proposed": [], "citizen": []}, label=f"{location} {districts} districts, > 40% POC", fontsize=10)
ax_bh_30 = histogram(ax_bh_30, {"ensemble":all_plan_shares["bh_30"], "proposed": [], "citizen": []}, label=f"{location} {districts} districts, > 30% BH", fontsize=10)
ax_bh_40 = histogram(ax_bh_40, {"ensemble":all_plan_shares["bh_40"], "proposed": [], "citizen": []}, label=f"{location} {districts} districts, > 40% BH", fontsize=10)


ax_poc_30.figure.savefig(f"{location}-districts-poc30.png", dpi = 500, bbox_inches = "tight")
ax_poc_40.figure.savefig(f"{location}-districts-poc40.png", dpi = 500, bbox_inches = "tight")
ax_bh_30.figure.savefig(f"{location}-districts-bh30.png", dpi = 500, bbox_inches = "tight")
ax_bh_40.figure.savefig(f"{location}-districts-bh40.png", dpi = 500, bbox_inches = "tight")

