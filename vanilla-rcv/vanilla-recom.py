import pandas as pd
from gerrychain.accept import always_accept
from gerrychain.chain import MarkovChain
from gerrychain.proposals import ReCom
from gerrychain.partition import MultiMemberPartition, Partition
from gerrychain.graph import Graph
from gerrychain.tree import recursive_tree_part
from gerrychain.updaters import Tally, cut_edges
from gerrychain.constraints import within_percent_of_ideal_population
from pathlib import Path
import jsonlines
import json
import sys
import math
import random
import numpy as np

from accept import (
    mh, mmpreference, districts as magnituder, totalseats, annealing,
    logistic, step, logicycle
)

from AnnealingConfiguration import AnnealingConfiguration

# Get the location we're working on and whether it's a "tilted" chain or not. The
# second argument should be either "tilted" or "neutral." 
districts = int(sys.argv[-1])
location = sys.argv[-2]


# Set some defaults.
POPCOL = "TOTPOP20"
EPSILON = 0.05
ITERATIONS = 1000
ASSIGNMENTS = True
SAMPLE = int(ITERATIONS*(1/10))
SAMPLEINDICES = [199, 399, 599, 799, 999]  #list(np.random.choice(range(0, ITERATIONS), size=SAMPLE, replace=False))

# For each of the locations, create relatively large ensembles. From these, we'll
# subsample.
# Read in the dual graph and the groupings.
G = Graph.from_json(f"./data/graphs/{location}.json")

# Find the ideal population.
totpop = sum(d[POPCOL] for _, d in G.nodes(data=True))
ideal = totpop/districts

# Create an assignment.
assignment = recursive_tree_part(
    G, range(districts), ideal, POPCOL, EPSILON
 )

# Updater for getting magnitude counts; also get the statewide POCVAP share.
counter = magnituder(totpop, districts)
pocvap = sum(d["POCVAP20"] for _, d in G.nodes(data=True))
vap = sum(d["VAP20"] for _, d in G.nodes(data=True))

# Create updaters.
updaters = {
    "population": Tally(POPCOL, "population"),
    "cut_edges": cut_edges,
    "POCVAP20": Tally("POCVAP20", "POCVAP20"),
    "VAP20": Tally("VAP20", "VAP20"),
    "BHVAP20": Tally("BHVAP20", "BHVAP20"),
    "WARREN18": Tally("WARREN18", "WARREN18"), 
    "DIEHL18": Tally("DIEHL18", "DIEHL18"), 
    "MAGNITUDE": lambda P: { d: counter(P["population"][d]) for d in P.parts },
    "SEATS": totalseats,
    "STEP": step
}

# Create the initial partition.
#seed_1 = pd.read_csv("good_seed_1.csv", dtype={"GEOID20":str}).set_index("GEOID20").to_dict()["assignment"]
#assignment = {n: seed_1[G.nodes[n]["id"]] for n in G.nodes}

initial = Partition(
    G, assignment=assignment, updaters=updaters
)

# Create the chain differently based on the type of chain we're running.
proposal = ReCom(POPCOL, ideal, EPSILON)
constraints = [
    within_percent_of_ideal_population(initial, EPSILON)
]

chain = MarkovChain(
    proposal=proposal, constraints=constraints, accept= always_accept,
    initial_state=initial, total_steps=ITERATIONS
)

# Create an empty list for plot data.
data = []
assignments = []
collectible = [
   "population", "POCVAP20", "VAP20", "BHVAP20", "WARREN18", "DIEHL18", "MAGNITUDE", "SEATS",
    "STEP"
] 

# Iterate over the chain and collect statistics.
for i, partition in enumerate(chain.with_progress_bar()):
    data.append({
        updater: partition[updater]
        for updater in collectible
    })

   
    # Also collect assignments!
    if ASSIGNMENTS: assignments.append(dict(partition.assignment))

# Write to file.
out = Path(f"./output/chains/{location}-{districts}-vanilla")

# If we aren't testing -- i.e. if this is a live run -- we save the data and the
# corresponding assignments to the appropriate location. Otherwise, we save the
# test data collected.
if not out.exists(): out.mkdir()

with jsonlines.open(out/f"neutral.jsonl", mode="w") as w:
    w.write_all(data)

if ASSIGNMENTS:
  with jsonlines.open(out/f"neutral-assignments.jsonl", mode="w") as w:
    w.write_all(assignments)
        
