import os, numpy as np, pandas as pd, matplotlib.pyplot as plt

# Funciones auxiliares
from practica_1.auxiliary import dump_pickle, load_pickle
# from auxiliary import dump_pickle, load_pickle, all_possible_combinations, stimuli_sequence

# Get the experiments
info_files = [arch for arch in os.listdir('practica_1/output_experimento_1') if 'info_experimental' in arch]
output_files = [arch for arch in os.listdir('practica_1/output_experimento_1') if 'output_participante' in arch]
questionary_files = [arch for arch in os.listdir('practica_1/output_experimento_1') if 'output_participante' in arch]

# for file in info_files:
#     info = load_pickle(path=os.path.join('practica_1/output_experimento_1/', file))
#     info['name'], file


# Iterate to get relevant data
results = {}
for out_file, info_file in zip(output_files, info_files):
    # Read output and get it sorted alphabetically
    output = load_pickle(path=os.path.join('practica_1/output_experimento_1/', out_file))
    info = load_pickle(path=os.path.join('practica_1/output_experimento_1/', info_file))
    stimuli_presented = sorted(list(output.keys()))

    # Get experiments where size is the changed category between train and trial
    size = [stimulus for stimulus in stimuli_presented if ('chico' in stimulus[0]) and ('grande' in stimulus[1])]
    size += [stimulus for stimulus in stimuli_presented if ('grande' in stimulus[0]) and ('chico' in stimulus[1])]
    
    # Now get experiments where animated is the changed category between train and trial
    living = [stimulus for stimulus in stimuli_presented if ('con vida' in stimulus[0]) and ('sin vida' in stimulus[1])]
    living += [stimulus for stimulus in stimuli_presented if ('sin vida' in stimulus[0]) and ('con vida' in stimulus[1])]
    
    # Get experiments where both categories change at the same time and then exclude them from size and living
    size_living = [stimulus for stimulus in stimuli_presented if (stimulus in living) and (stimulus in size)]
    living = [stimulus for stimulus in living if stimulus not in size_living]
    size = [stimulus for stimulus in size if stimulus not in size_living]

    # Analyze each type of experiment
    results[info['name']] = []
    for _, tested_stimulus in stimuli_presented:
        results[info['name']].append((_.removesuffix(' en relación con una persona promedio'),tested_stimulus.removesuffix(' en relación con una persona promedio')))
    for experiment in [living, size, size_living]:
        for _, tested_stimulus in experiment:
            results[info['name']].append((_.removesuffix(' en relación con una persona promedio'),tested_stimulus.removesuffix(' en relación con una persona promedio')))
        # for categories in experiment:
        #     llaves = list(output[categories].keys())
        #     output[categories][llaves[0]]==output[categories][llaves[1]]

        # See if there is a difference between presenting one category first (i.e. its the same to present 'chico', then 'grande' and 'grande', then 'chico'?)
        first_train, first_test = output[experiment[0]]['train'], output[experiment[0]]['test']
        
        first_train==first_test # TODO (ups)
        
        first_train['response_time(s)']
        first_test['response_time(s)']


lista = ['con vida y chico en relación con una persona promedio', 'con vida y grande en relación con una persona promedio', 'con vida y grande en relación con una persona promedio', 'sin vida y grande en relación con una persona promedio', 'sin vida y grande en relación con una persona promedio', 'con vida y grande en relación con una persona promedio']
for sub in results:
    results[sub]