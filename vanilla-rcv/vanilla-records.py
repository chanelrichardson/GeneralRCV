
import jsonlines
import us
import sys
from pathlib import Path
import json

loc_add = 0
districts = sys.argv[-1] 
location = us.states.lookup(sys.argv[-2+loc_add].title(), field="name")


read = Path(f"./output/chains/{location.name.lower()}-{districts}-vanilla/neutral.jsonl")
write = Path(f"./output/records/{location.name.lower()}-{districts}-vanilla")

# Cread in plan data and create an empty list of records.
with jsonlines.open(read) as r: plans = list(r)
records = []

# Get the number of districts in the state.
districts = sum(plans[0]["MAGNITUDE"].values())

# For each of the plans, "invert" the dictionaries so organized by district->properties,
# not properties->district.
for plan in plans:
    dkeys = list(plan["population"])

    # Get all the standard stuff.
    record = {
        district: {
            prop: plan[prop][district]
            for prop in ["population", "POCVAP20", "VAP20", "WARREN18", "DIEHL18", "MAGNITUDE", "BHVAP20"]
        }
        for district in dkeys
    }

    # Get the POCVAP percentage.
    for district in dkeys:
        record[district]["POCVAP20%"] = record[district]["POCVAP20"]/record[district]["VAP20"]
        record[district]["BHVAP20%"] = record[district]["BHVAP20"]/record[district]["VAP20"]
        record[district]["WARREN18%"] = record[district]["WARREN18"]/(record[district]["WARREN18"] + record[district]["DIEHL18"])
    # Get the number of "POC seats"
    for district in dkeys:
        threshold = 1/(record[district]["MAGNITUDE"]+1)
        record[district]["BHSEATS"] = record[district]["BHVAP20%"]//threshold
        record[district]["POCSEATS"] = record[district]["POCVAP20%"]//threshold
        record[district]["DEMSEATS"] = record[district]["WARREN18%"]//threshold
    records.append(record)

# Write back to file.
if not write.exists(): write.mkdir()
with jsonlines.open(write/f"neutral.jsonl", mode="w") as w: w.write_all(records)
