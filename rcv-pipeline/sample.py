
from gerrychain.accept import always_accept
from gerrychain.chain import MarkovChain
from gerrychain.proposals import ReCom
from gerrychain.partition import MultiMemberPartition
from gerrychain.graph import Graph
from gerrychain.tree import recursive_tree_part
from gerrychain.updaters import Tally, cut_edges, Election
from gerrychain.constraints import within_percent_of_ideal_population_per_representative
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
# The third argument is the magnitude list. This is a list where index 0 
# is the number of magnitude 3 districts, index 1 is the number of magnitude
# 4 districts, and index 2 is the number of magnitude 5 districts. 
# i.e. "[0, 10, 0]" to give 10, 4 member districts.

location = sys.argv[-3]
chaintype = sys.argv[-2]
mag_list = json.loads(sys.argv[-1])

tilted = chaintype == "tilted"
mag_str = f"{mag_list[0]}-{mag_list[1]}-{mag_list[2]}"

# Read in configuration information if we're running a tilted chain.
if tilted:
    with open("config.json") as r: config = json.load(r)
    configuration = AnnealingConfiguration(**config[location])

# Set some defaults.
POPCOL = "TOTPOP20"
EPSILON = 0.05
ITERATIONS = 1000
ASSIGNMENTS = True
SAMPLE = int(ITERATIONS*(1/10))
SAMPLEINDICES = list(np.random.choice(range(0, ITERATIONS), size=SAMPLE, replace=False))
TEST = False

# For each of the locations, create relatively large ensembles. From these, we'll
# subsample.
# Read in the dual graph and the groupings.
G = Graph.from_json(f"./data/graphs/{location}.json")
with open("./groupings.json") as f: info = json.load(f)

# Explode the districts.
# Currently the optimal grouping comes from running groupings.py
# on your location, BUT this gives you FairVote's optimal grouping. 
# The best way to override this is to change what the optimal
# grouping is in the file itself. It COULD be another argument, 
# but that's starting to feel a bit lengthy :/.
districts = info[location]["districts"]
#grouping = info[location]["optimal"]

# For the optimal grouping, create a dictionary that maps 
# district numbers to their magnitudes.

magnitudes = {}
last = 1
for magnitude, number in zip([3, 4, 5], mag_list):
    for i in range(number):
        magnitudes[last] = magnitude
        last += 1

members = sum(magnitudes.values())
districts = list(magnitudes.keys())

# Find the ideal population.
totpop = sum(d[POPCOL] for _, d in G.nodes(data=True))
ideal = totpop/members

# Create an assignment.
assignment, magnitudes = recursive_tree_part(
    G, districts, ideal, POPCOL, EPSILON, magnitudes=magnitudes
)

# Updater for getting magnitude counts; also get the statewide POCVAP share.
counter = magnituder(totpop, members)
pocvap = sum(d["POCVAP20"] for _, d in G.nodes(data=True))
vap = sum(d["VAP20"] for _, d in G.nodes(data=True))

# Create updaters.
# Currently, some of these updaters are MA specific, 
# but update with whatever you want to track in your
# chain.

updaters = {
    "population": Tally(POPCOL, "population"),
    "cut_edges": cut_edges,
    "POCVAP20": Tally("POCVAP20", "POCVAP20"),
    "BHVAP20": Tally("BHVAP20", "BHVAP20"),
    "VAP20": Tally("VAP20", "VAP20"),
    "WARREN18": Tally("WARREN18", "WARREN18"),
    "DIEHL18": Tally("DIEHL18", "DIEHL18"),
    "PREFERENCE": mmpreference("POCVAP20", "VAP20", pocvap/vap),
    "MAGNITUDE": lambda P: { d: counter(P["population"][d]) for d in P.parts },
    "SEATS": totalseats,
    "STEP": step
}

if tilted:
    updaters.update({
        "ANNEAL": annealing(
            "SEATS",
            logicycle(
                configuration.max,              # maximum (minimum) temperature
                configuration.growth,           # logistic growth rate
                ITERATIONS,
                configuration.midpoint,         # where the cycle hits its "peak"
                cycles=configuration.cycles,    # number of cycles across the chain
                cold=configuration.cold         # number of steps we stay at the max (min) temp per cycle
            ),
            step="STEP",
            maximize=True
        )
    })


# Create the initial partition.
initial = MultiMemberPartition(
    G, assignment=assignment, updaters=updaters, magnitudes=magnitudes
)


# Create the chain differently based on the type of chain we're running.
proposal = ReCom(POPCOL, ideal, EPSILON, multimember=True)
constraints = [
    within_percent_of_ideal_population_per_representative(initial, EPSILON)
]

def tentative(score):
    def _(P):
        return min(P[score], 1) >= random.random()
    return _

chain = MarkovChain(
    proposal=proposal, constraints=constraints, accept=tentative("ANNEAL") if tilted else always_accept,
    initial_state=initial, total_steps=ITERATIONS
)

# Create an empty list for plot data.
data = []
assignments = []
collectible = ["population", "POCVAP20", "BHVAP20", "VAP20", "WARREN18", "DIEHL18", "MAGNITUDE", "PREFERENCE", "SEATS","STEP"] + (["ANNEAL"] if tilted else []) 

if TEST:
    seatcounts = []
    anneal = []
    preference = []

# Iterate over the chain and collect statistics.
for i, partition in enumerate(chain.with_progress_bar()):
    data.append({
        updater: partition[updater]
        for updater in collectible
    })

    # If we're testing for annealing configurations, get them here.
    if TEST:
        seatcounts.append(partition["SEATS"])
        preference.append(partition["PREFERENCE"])
        if tilted: anneal.append(partition["ANNEAL"])

    # Also collect assignments!
    if ASSIGNMENTS and i in SAMPLEINDICES: assignments.append(dict(partition.assignment))

# Write to file.
out = Path(f"./output/chains/{location}-{mag_str}")

# If we aren't testing -- i.e. if this is a live run -- we save the data and the
# corresponding assignments to the appropriate location. Otherwise, we save the
# test data collected.
if not out.exists(): out.mkdir()

if not TEST:
    with jsonlines.open(out/f"{chaintype}.jsonl", mode="w") as w:
        w.write_all(data)

    if ASSIGNMENTS:
        with jsonlines.open(out/f"{chaintype}-assignments.jsonl", mode="w") as w:
            w.write_all(assignments)
else:
    with open(out/f"{chaintype}-seats.json", "w") as w: json.dump(seatcounts, w)
    with open(out/f"{chaintype}-anneal.json", "w") as w: json.dump(anneal, w)
    with open(out/f"{chaintype}-preference.json", "w") as w: json.dump(preference, w)
        
