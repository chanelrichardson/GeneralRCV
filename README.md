# RCV PIPELINE OVERVIEW 
**While this is called GeneralRCV, this pipeline has only been used in Massachusetts.**


## Flow for creating an ensemble, and running RCV simulation.


### `sample.py`

In order to use this file, you'll need to run this: 
`pip install git+https://github.com/jenni-niels/GerryChain@multi-member-recom`

Within this file, we're running a chain that makes multimember partitions of the provided graph. This file calls on the graph for the location provided in the arguments. All graphs were created by Anthony Pizzimenti and are available in data/graphs. I believe all of these are vtd level graphs. 

There's some parameters that are set within the file. These are things like `TEST`. When set to True, this script will output different files for the chain (a seats file, annealing file, and )

This file is currently also set up to take a subsample of plans from a full chain run. The reason this is set to so few plans, is because further down the line, the time increases significantly. Further explanation in the `rcv-simulation.py` section. 

You can also change the `EPSILON` for the districts created and the `ITERATIONS` (number of steps in the chain). 

**Arguments** 

`python sample.py [location] [chaintype] [mag_list]`

* location - state that you’re creating an ensemble for
* chaintype - determines whether you’re running a neutral chain (always accept the next step) or a tilted (annealing) chain (accept probabilistically)
* mag_list - a list of numbers that denotes the number of 3 member, 4 member, and 5 member districts. I.e. “[8, 0, 0]” would create 8 3 member districts.

Within the code, a list of updaters is set for the run. These updaters are currently hard-coded for MA, but can be changed to track your desired metrics.

**Output**

You’ll get {chaintype}.jsonl and {chaintype}-assignments.jsonl (If ASSIGNMENTS is set to True within the code). The {chaintype}.jsonl will contain all of the updater information for each step. i.e. district level values for “VAP20”, “POCVAP20”, etc. at every step.

The assignments file maps node ids to district assignments. **Note that these are not GEOIDs**, and you’ll have to work with the graph to recover which node id maps to which GEOID. 



### `score-records.py` 
Takes the scores output from the original `sample.py` file, and reformats them for further use. 

**Arguments**

`python score-records.py [location] [bias] [mag_list]`

* location -state that you want to score an ensemble for
* bias - denotes whether you’re scoring a neutral or tilted ensemble
* mag_list - a list of numbers that denotes the number of 3 member, 4 member, and 5 member districts for the configuration you’re scoring. 

**Output**
This gives the same scores as {chaintype}.jsonl in a more structured format.

### `make-config.py`
The configuration file is used within the RCV simulation to define a variety of parameters. These
specific parameters and their descriptions can be found in `ModelingConfiguration.py`. The parameters 
currently in this file are all specific to Massachusetts, so be sure to change them accordingly. This file 
was also created for MA modeling, and I'm not sure how configuration files were created for the FairVote
project.

The configuration is a large dictionary. At the top level there's one key per state. The configuration file
doesn't need to include all 50 states, just the states you want to run on. 

For each state there is a "neutral" dictionary and a "tilted" dictionary to define configurations for both
types of ensembles. 

The configuration files are made from the ensembles, so the length of configuration["state"][chaintype] is the number of 
plans in the ensemble. 

configuration["state"][chaintype][0] will give a dictionary of configurations for each district in a plan. So if there are 8 districts, regardless of size len(configuration["state"][chaintype]) would equal 8. 

Finally, you set one ModelingConfiguration option for each configuration you want to run for a district. For a single district 
you may want to vary the model type, or something else. When all of the results are aggregated, all configurations will be 
combined, so keep that in mind. For example, you wouldn't want to aggregate rcv-simulations where there's a different number of total seats available, because it wouldn't be an accurate comparison.

**Arguments**

`python make-config.py [location] [mag_list]`

* location - state to make a configuration for
* mag_list - a list of numbers that denotes the number of 3 member, 4 member, and 5 member districts for the configuration you’re creating a configuration for. 

**Output**
Jsonl file that has a configuration for a state. 


### `rcv-simulation.py`
Runs the actual RCV simulation on your plan (only does one plan at a time, so you have to run this script for each of the indvidual plans in the ensemble). This models all configurations detailed in the configuration file you just created. 

This interfaces largely with a lot of inner workings of the specific election models. The behind the scenes work is happening in `model_details.py`. I'm not as familiar with this file, and haven't altered it. 

In running this, the imports from the `accept.py` file gave me issues at various times. I never really figured out the issue/how to fix without just continuing to re-run this simulation file until it worked (but it always worked eventually).

**Arguments**

`python rcv-simulation.py [location] [BIAS] [INDEX] [MAG_LIST]`

* location - state you're simulating RCV elections on
* BIAS - the type of chain you're running RCV on (neutral or tilted)
* INDEX - index of the plan within the ensemble you're running a simulation on
* MAG_LIST - a list of numbers that denotes the number of 3 member, 4 member, and 5 member districts for the configuration you’re running a simulation on. 

**Output**
* jsonl file with ModelingResult objects (more information can be found in ModelingResult.py). These are similar to ModelingConfiguration objects, but include an extra piece of information about number of seats won by POC preferred candidates. 

### `plots-by-model-combined.py`

Creates plots visualizing the number of POC preferred seats won within the ensemble.

**Arguments**

`python plots-by-model-combined.py [location] [mag_list]` 

* location - state you're creating a plot for
* mag_list - a list of numbers that denotes the number of 3 member, 4 member, and 5 member districts for the configuration you’re plotting

**Output**
An image visualizing each of the models and the number of seats won by POC preferred candidates across plans. 


Other python files are included in this repository that have not been changed nor used by me. I kept around files that were available in Anthony’s original “FairVote-FRA” repository available at github.com/mggg/FairVote-FRA.


Creating an ensemble + running RCV simulation on an ensemble created by nesting into a specific plan. 


## Flow for creating an ensemble, and running RCV simulation when nesting into a specific plan. 

This pipeline defaults to creating an ensemble of plans that are nested into the last plan of the tilted ensemble. 

### `nested-sample.py`

**Arguments** 
* location - state that you’re creating an ensemble for
* chaintype - determines whether you’re running a neutral chain (always accept the next step) or a tilted (annealing) chain (accept probabilistically)
* assignment_num - corresponds to the district in the original chain to nest into. For example, if you're creating the set of districts that nests into district 1 of your original plan, then the assignment_num would be 1. 
* mag_list - a list of numbers that denotes the number of 3 member, 4 member, and 5 member districts **of the chain you're nesting into**. I.e. “[8, 0, 0]” would create 8 3 member districts.
* nested_mag_list - a list of numbers that denote the number of 3 member, 4 member, and 5 member districts in the chain you're creating. 

Within the code, a list of updaters is set for the run. These updaters are currently hard-coded for MA, but can be changed to track your desired metrics.

**Output** 

You’ll get {chaintype}-{assignment_num}.jsonl and {chaintype}-assignments-{assignment_num}.jsonl (If ASSIGNMENTS is set to True within the code). The {chaintype}.jsonl will contain all of the updater information for each step. i.e. district level values for “VAP20”, “POCVAP20”, etc. at every step.

The assignments file maps node ids to district assignments. **Note that these are not GEOIDs**, and you’ll have to work with the graph to recover which node id maps to which GEOID. 

### `coalesce.py`

Takes all the separate assignments and records from the nested-sample output and combines them into singular files.

**Arguments**
* location - state that you’re coalescing info for
* chaintype - neutral or tilted chain
* mag_list - a list of numbers that denotes the number of 3 member, 4 member, and 5 member districts **of the new chain just created**

**Output**
You'll get {chaintype}.jsonl and {chaintype}-assignments.jsonl files that are combined over all districts. 


### `score-records.py` 
**Arguments**
* location -state that you want to score an ensemble for
* bias - denotes whether you’re scoring a neutral or tilted ensemble
* mag_list - a list of numbers that denotes the number of 3 member, 4 member, and 5 member districts for the configuration you’re scoring. 
* --nested - a flag that you need to include for this, the flag ensures you aren't overwriting scores from a non-nested configuration with the same magnitude list.

### Output 
This gives the same scores as {chaintype}.jsonl in a more structured format.

### `make-config.py`
The configuration file is used within the RCV simulation to define a variety of parameters. These
specific parameters and their descriptions can be found in `ModelingConfiguration.py`.

The configuration is a large dictionary. At the top level there's one key per state. The configuration file
doesn't need to include all 50 states, just the states you want to run on. 

For each state there is a "neutral" dictionary and a "tilted" dictionary to define configurations for both
types of ensembles. 

The configuration files are made from the ensembles, so the length of configuration["state"][chaintype] is the number of 
plans in the ensemble. 

configuration["state"][chaintype][0] will give a dictionary of configurations for each district in a plan. So if there are 8 districts, regardless of size len(configuration["state"][chaintype]) would equal 8. 

Finally, you set one ModelingConfiguration option for each configuration you want to run for a district. For a single district 
you may want to vary the model type, or something else. When all of the results are aggregated, all configurations will be 
combined, so keep that in mind. For example, you wouldn't want to aggregate rcv-simulations where there's a different number of total seats available, because it wouldn't be an accurate comparison.

**Arguments**
* location - state to make a configuration for
* mag_list - a list of numbers that denotes the number of 3 member, 4 member, and 5 member districts for the configuration you’re creating a configuration for. 
* --nested - a flag that you need to include for this, the flag ensures you aren't overwriting scores from a non-nested configuration with the same magnitude list.

**Output**
Jsonl file that has a configuration for a state. 


### `rcv-simulation.py`
Runs the actual RCV simulation on your plan. This models all configurations detailed in the configuration file you just created. 

**Arguments**
* location - state you're simulating RCV elections on
* BIAS - the type of chain you're running RCV on (neutral or tilted)
* INDEX - index of the plan within the ensemble you're running a simulation on
* MAG_LIST - a list of numbers that denotes the number of 3 member, 4 member, and 5 member districts for the configuration you’re running a simulation on. 
* --nested - a flag that you need to include for this, the flag ensures you aren't overwriting scores from a non-nested configuration with the same magnitude list.

**Output**
* jsonl file with ModelingResult objects (more information can be found in ModelingResult.py). These are similar to ModelingConfiguration objects, but include an extra piece of information about number of seats won by POC preferred candidates. 

### `plots-by-model-combined.py`

Creates plots visualizing the number of POC preferred seats won within the ensemble.

**Arguments**
* location - state you're creating a plot for
* mag_list - a list of numbers that denotes the number of 3 member, 4 member, and 5 member districts for the configuration you’re plotting
* --nested - a flag that you need to include for this, the flag ensures you aren't overwriting scores from a non-nested configuration with the same magnitude list.

**Output**
An image visualizing each of the models and the number of seats won by POC preferred candidates across plans. 

## Vanilla Recom
A separate folder exists here called vanilla-rcv which does a regular vanilla recom run in the same style as the rest of the RCV pipeline 

### `vanilla-recom.py`

Corresponds to `sample.py`. 

Similarly, there are parameters to be set manually within the code (they are the same parameters mentioned above).

I've only set this up to do neutral runs, this also doens't have region_aware support. 

**Arguments**
* location - state you're running recom on
* districts - number of districts to create

**Output** 
Two outputs, one with the information tracked in the updaters for every plan in the ensemble. The other file contains assignments from graph node ids to assignments. 

### `vanilla-records.py`

Reformats the records from `vanilla-recom.py`. 

**Arguments**
* location - state you're getting records for
* districts - number of districts in the plan you're getting records for. 

### `vanilla-config.py`

Creates the file of ModelingConfiguration results to be used for rcv simulation. 

**Arguments**
* location - state you're making a configuration file for
* dsitricts - number of districts in the plan you're creating a configuration file for. 

### `vanilla-sim.py`

Runs the rcv simulation on the vanilla plan. Will need to run this file individually for each plan in the ensemble.

**Arguments**
* location - state you're running rcv simulation on
* INDEX - index for the plan you're running on. 
* districts - number of districts in the plan you're doing rcv simulation on. 

**Output** 
Files for each plan with ModelingResult objects that contain the number of seats won by POC preferred candidates in each district of the plan for each configuration scenario.

### `vanilla-plots.py`

Creates the seats plot for the vanilla recom plans. I'm not sure why, but I haven't gotten this one to work. 

**Arguments**
* location - state to create the plot for
* totmembers - number of districts in the plan

**Output**
*Ideally* the seats plot for the vanilla recom run. 





**Other python files are included in this repository that have not been changed nor used by me. I kept around files that are available in Anthony’s original “FairVote-FRA” repository available at github.com/mggg/FairVote-FRA.**







