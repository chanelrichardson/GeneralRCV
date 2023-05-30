
import jsonlines
import json
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.font_manager import FontProperties
from matplotlib.lines import Line2D
from pathlib import Path
import us
import os
import sys
import pandas as pd
import numpy as np
from collections import Counter
import warnings
warnings.filterwarnings("ignore")
from ModelingResult import ModelingResult, aggregate

# Get the location for the chain and the bias.
config_str = sys.argv[-1]
totmembers = int(sys.argv[-2])
location = us.states.lookup(sys.argv[-3].title(), field="name")
focus = { us.states.FL, us.states.IL, us.states.MA, us.states.MD, us.states.TX }

# Get the configuration for the state.
poc = pd.read_csv("./data/demographics/pocrepresentation.csv")
statewide = pd.read_csv("./data/demographics/summary.csv")

summary = statewide.merge(poc, on="STATE")\
    .set_index("STATE")\
    .to_dict("index")

state = summary[location.name.title()]

REDUCEDTURNOUT = True
turnoutsuffix = ""
if REDUCEDTURNOUT: turnoutsuffix = "_low_turnout"
# Load the plans for the ensemble.
output = Path("./output/")
planpath = Path(output/f"results/{location.name.lower()}/{location.name.lower()}-{totmembers}-vanilla-{config_str}/")

ensembletypes = ["neutral"]
tilted = False


# Create a mapping for configurations.
concentrations = {
    "A": [0.5]*4,               # Voters more or less agree on candidate order for each group.
    "B": [1]*4,       # Every voter is equally likely to vote for every candidate. 
    "C": [0.5, 1, 1, 0.5],      # POC voters agree on POC preferred candidates, White voters agree on White preferred candidates. 
    "D": [0.5,2,2,0.5],         # POC voters agree on POC pref, and white voters agree on White pref, stronger disagreement otherwise.
    # "E": [1]*4                  # No agreement or disagreement --- it's pandemonium.
}


# Bucket for ensembles.
ensembles = []

for ensembletype in ensembletypes:
    # Bucket for plans.
    plans = []

    # Check to see whether we have the complete results.
    tpath = planpath/f"{ensembletype}-1.jsonl"
    representatives = totmembers

    if tpath.exists() or True:
        for plan in range(5 if representatives > 5 else 10):
            try:
                districts = []
                with jsonlines.open(planpath/f"{ensembletype}-{plan}.jsonl") as r:
                    for district in r:
                        C = [ModelingResult(**c) for c in district]

                        for c in C:
                            for name, concentration in concentrations.items():
                                if c.concentration == concentration:
                                    c.concentrationname = name

                        districts.append(C)
            except: continue
            plans.append(districts)
    else:
        with jsonlines.open(planpath/f"{ensembletype}.jsonl") as r:
            for plan in r:
                districts = []
                for district in plan.values():
                    C = [ModelingResult(**c) for c in district]

                    for c in C:
                        for name, concentration in concentrations.items():
                            if c.concentration == concentration: c.concentrationname = name
                    districts.append(C)
                plans.append(districts)

        # Cascade!
        plans.append(districts)
    ensembles.append(plans)

models = ["plackett-luce", "bradley-terry", "crossover", "cambridge"]
concentrations = ["A", "B", "C", "D"]

# Sample size.
subsample = 3

# Aggregate results.
neutralresults = aggregate(ensembles[0], models, concentrations, subsample=subsample)
print(neutralresults)
if tilted: tiltedresults = aggregate(ensembles[1], models, concentrations, subsample=subsample)

# Merge the dictionaries!
modelresults = {
    model: neutralresults[model] + (tiltedresults[model] if tilted else [])
    for model in models + ["all"]
}

# Counting!
modelresults = {
    name: {
        seats: count/len(model)
        for seats, count in dict(Counter(model)).items()
    }
    for name, model in modelresults.items()
}

# Get everything.
modelresults["alt. crossover"] = modelresults["crossover"]
modelresults["Combined"] = modelresults["all"]
del modelresults["all"]
del modelresults["crossover"]

modelresults = {
    model: modelresults[model]
    for model in ["plackett-luce", "bradley-terry", "alt. crossover", "cambridge", "Combined"]
}

# Create plots.
fig, ax = plt.subplots(figsize=(15, 7.5))

# Plotting! Here, we want to make circles at the appropriate height by summing
# over the seat totals from the *plans*. Set some defaults, like the max radius
# of the circles.
r = 1/2
y = 2
ymax = 13
xmax, xmin = 0, 10000

# Some defaults for circles.
cdefs = dict(
    linewidth=3/4,
    edgecolor="grey",
    zorder=1
)

print(modelresults)
for name, model in modelresults.items():
    for x, share in model.items():
        # Get the appropriate radius relative to the max radius.
        sr = r*np.sqrt(share)
        print(share, sr)
        # Plot a circle!
        color = "steelblue" if name == "Combined" else "mediumpurple"
        C = Circle((x, ymax-(y+1) if name == "Combined" else ymax-y), sr, facecolor=color)
        ax.add_patch(C)

        if xmax < x: xmax = x
        if xmin > x: xmin = x
    
    y+=2

# Set proportionality line and Biden support line!
ax.axvline(totmembers*state["POCVAP20%"], color="gold", alpha=1/2)
ax.axvline(totmembers*(state["2018_WARREN_D"]/(state["2018_WARREN_D"] + state["2018_WARREN_R"])), 
    color="olivedrab", alpha=1/2)
ax.axvline(
    totmembers*(state["2020_PRES_D"]/(state["2020_PRES_D"]+state["2020_PRES_R"])),
    color="slategray", alpha=1/2
)

# Re-set the xmin value if the number of POC representatives is smaller than everything!
# Really unlikely that the current number is bigger than everything.
xmin = 0

# Set labels!
#pos = list(range(1, x+1))
labellocs = [2, 5, 7, 9, 11]

# Set label and ticklabel font properties.
lfp = FontProperties(family="Playfair Display")
lfd = {"fontproperties": lfp}
fp = FontProperties(family="CMU Serif")


for m, loc in zip(modelresults.keys(), reversed(labellocs)):
    if m == "crossover": m = "alt. crossover"
    ax.text(
        xmin-6/5, loc+1/4, m.title(), fontsize=10, ha="right", va="top", fontdict=lfd
    )

# Put a break between the model results and the combined results.
# ax.axhline(5, color="k", alpha=1/2, ls=":")

# Take away x-tick values and x-tick markers.
ax.axes.get_yaxis().set_visible(False)

# Set plot limits.
ax.set_xlim(0, round(totmembers*0.75))
ax.set_ylim(0, y+1)
#xticks = list(range(xmin, xmax+1))

if totmembers < 10:
  xticks = list(range(round(totmembers*0.75)))
  ax.set_xticks(xticks, [str(int(x)) for x in xticks])
elif 10 <= totmembers <= 50:
  xticks = list(range(round(totmembers*0.75)))
  ax.set_xticks(xticks[::5],
                [str(int(x)) for x in range(round(totmembers*0.75)) if x%5 == 0])
else:
  xticks = list(range(round(totmembers*0.75)))
  ax.set_xticks(xticks[::10],
                [str(int(x)) for x in range(round(totmembers*0.75)) if x%10 == 0])
  

# Set aspects equal.
ax.set_aspect("equal")

# Now go through and set font properties? this is bullshit
for tickset in [ ax.get_xticklabels()]:
    for tick in tickset:
        tick.set_fontproperties(fp)

# Set axis labels.
ax.set_xlabel("Statewide Seats", fontdict=lfd)

# Add a legend?
handles = [
    Line2D([0],[0], color="gold", alpha=1/2, label="POC proportionality"),
    Line2D([0],[0], color="k", alpha=1/2, label="Biden proportionality"),
    Line2D([0],[0], color="forestgreen", alpha=1/2, label="Warren proportionality")
]

ax.legend(
    prop=FontProperties(family="Playfair Display", size=7),
    title_fontproperties=FontProperties(family="Playfair Display", size=9),
    title="Detailed seat projection", handles=handles, ncol=2,
    borderaxespad=0, loc="lower center", bbox_to_anchor=(0.5, 1.05)
)

bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
width, height = bbox.width, bbox.height

figpath = f"./output/figures/nationwide/{location}/ma-{totmembers}-vanilla"

os.makedirs(figpath, exist_ok=True)
plt.savefig(f"{figpath}/plots-by-model-combined-{totmembers}-vanilla-{config_str}.png", dpi=600, bbox_inches="tight")
