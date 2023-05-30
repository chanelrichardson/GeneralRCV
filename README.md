#RCV PIPELINE OVERVIEW 

## Flow for creating an ensemble, and running RCV simulation.

`sample.py`

### Arguments 
* location - state that you’re creating an ensemble for
* chaintype - determines whether you’re running a neutral chain (always accept the next step) or a tilted (annealing) chain (accept probabilistically)
* mag_list - a list of numbers that denotes the number of 3 member, 4 member, and 5 member districts. I.e. “[8, 0, 0]” would create 8 3 member districts.

Within the code, a list of updaters is set for the run. These updaters are currently hard-coded for MA, but can be changed to track your desired metrics.

### Output 

You’ll get {chaintype}.jsonl and {chaintype}-assignments.jsonl (If ASSIGNMENTS is set to True within the code). The {chaintype}.jsonl will contain all of the updater information for each step. i.e. district level values for “VAP20”, “POCVAP20”, etc. at every step.

The assignments file maps node ids to district assignments. **Note that these are not GEOIDs**, and you’ll have to work with the graph to recover which node id maps to which GEOID. 


‘score-records.py’ 
### Arguments
* location -state that you want to score an ensemble for
* bias - denotes whether you’re scoring a neutral or tilted ensemble
* mag_list - a list of numbers that denotes the number of 3 member, 4 member, and 5 member districts for the configuration you’re scoring. 

### Output 
This gives the same scores as {chaintype}.jsonl in a more structured format.

`make-config.py`
Arguments


`rcv-simulation.py`
Arguments

`plots-by-model-combined.py`
Arguments

Other python files are included in this repository that have not been changed nor used by me. I kept around files that were available in Anthony’s original “FairVote-FRA” repository available at github.com/mggg/FairVote-FRA.


Creating an ensemble + running RCV simulation on an ensemble created by nesting into a specific plan. 


#RCV PIPELINE OVERVIEW 

## Flow for creating an ensemble, and running RCV simulation.

`sample.py`

### Arguments 
* location - state that you’re creating an ensemble for
* chaintype - determines whether you’re running a neutral chain (always accept the next step) or a tilted (annealing) chain (accept probabilistically)
* mag_list - a list of numbers that denotes the number of 3 member, 4 member, and 5 member districts. I.e. “[8, 0, 0]” would create 8 3 member districts.

Within the code, a list of updaters is set for the run. These updaters are currently hard-coded for MA, but can be changed to track your desired metrics.

### Output 

You’ll get {chaintype}.jsonl and {chaintype}-assignments.jsonl (If ASSIGNMENTS is set to True within the code). The {chaintype}.jsonl will contain all of the updater information for each step. i.e. district level values for “VAP20”, “POCVAP20”, etc. at every step.

The assignments file maps node ids to district assignments. **Note that these are not GEOIDs**, and you’ll have to work with the graph to recover which node id maps to which GEOID. 


‘score-records.py’ 
### Arguments
* location -state that you want to score an ensemble for
* bias - denotes whether you’re scoring a neutral or tilted ensemble
* mag_list - a list of numbers that denotes the number of 3 member, 4 member, and 5 member districts for the configuration you’re scoring. 

### Output 
This gives the same scores as {chaintype}.jsonl in a more structured format.

`make-config.py`
Arguments


`rcv-simulation.py`
Arguments

`plots-by-model-combined.py`
Arguments

Other python files are included in this repository that have not been changed nor used by me. I kept around files that were available in Anthony’s original “FairVote-FRA” repository available at github.com/mggg/FairVote-FRA.


Creating an ensemble + running RCV simulation on an ensemble created by nesting into a specific plan. 





