# RCV PIPELINE OVERVIEW 

## Flow for creating an ensemble, and running RCV simulation.

### `sample.py`

**Arguments** 
* location - state that you’re creating an ensemble for
* chaintype - determines whether you’re running a neutral chain (always accept the next step) or a tilted (annealing) chain (accept probabilistically)
* mag_list - a list of numbers that denotes the number of 3 member, 4 member, and 5 member districts. I.e. “[8, 0, 0]” would create 8 3 member districts.

Within the code, a list of updaters is set for the run. These updaters are currently hard-coded for MA, but can be changed to track your desired metrics.

**Output**

You’ll get {chaintype}.jsonl and {chaintype}-assignments.jsonl (If ASSIGNMENTS is set to True within the code). The {chaintype}.jsonl will contain all of the updater information for each step. i.e. district level values for “VAP20”, “POCVAP20”, etc. at every step.

The assignments file maps node ids to district assignments. **Note that these are not GEOIDs**, and you’ll have to work with the graph to recover which node id maps to which GEOID. 


### `score-records.py` 
**Arguments**
* location -state that you want to score an ensemble for
* bias - denotes whether you’re scoring a neutral or tilted ensemble
* mag_list - a list of numbers that denotes the number of 3 member, 4 member, and 5 member districts for the configuration you’re scoring. 

**Output**
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

**Output**
Jsonl file that has a configuration for a state. 


### `rcv-simulation.py`
Runs the actual RCV simulation on your plan. This models all configurations detailed in the configuration file you just created. 

**Arguments**
* location - state you're simulating RCV elections on
* BIAS - the type of chain you're running RCV on (neutral or tilted)
* INDEX - index of the plan within the ensemble you're running a simulation on
* MAG_LIST - a list of numbers that denotes the number of 3 member, 4 member, and 5 member districts for the configuration you’re running a simulation on. 

**Output**
* jsonl file with ModelingResult objects (more information can be found in ModelingResult.py). These are similar to ModelingConfiguration objects, but include an extra piece of information about number of seats won by POC preferred candidates. 

### `plots-by-model-combined.py`

Creates plots visualizing the number of POC preferred seats won within the ensemble.

**Arguments**
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


**Other python files are included in this repository that have not been changed nor used by me. I kept around files that are available in Anthony’s original “FairVote-FRA” repository available at github.com/mggg/FairVote-FRA.**







