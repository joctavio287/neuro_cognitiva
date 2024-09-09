import pickle, os, csv, numpy as np, random
from random import shuffle

import psychopy as psy

def load_pickle(path:str):
    """Loads pickle file

    Parameters
    ----------
    path : str
        Path to pickle file

    Returns
    -------
    _type_
        Extracted file

    Raises
    ------
    Exception
        Something goes wrong, probably it's not a .pkl
    Exception
        The file doesn't exist
    """
    if os.path.isfile(path):
        try:
            with open(file = path, mode = "rb") as archive:
                data = pickle.load(file = archive)
            return data
        except:
            raise Exception("Something went wrong, check extension.")
    else:
        raise Exception(f"The file '{path}' doesn't exist.")
    
def dump_pickle(path:str, obj, rewrite:bool=False, verbose:bool=False):
    """Dumps object into pickle

    Parameters
    ----------
    path : str
        Path to pickle file
    obj : _type_
        Object to save as pickle. Almost anything
    rewrite : bool, optional
        If already exists a file named as path it rewrites it, by default False
    verbose : bool, optional
        Whether to print information about rewritting, by default False

    Raises
    ------
    Exception
        If the file already exists and rewrite wasnt called.
    Exception
        Something went wrong.
    """
    isfile = os.path.isfile(path)
    if isfile and not rewrite:
        raise Exception("This file already exists, change 'rewrite=True'.")
    try:
        with open(file = path, mode = "wb") as archive:
            pickle.dump(file = archive, obj=obj)
        if isfile and verbose:
            print(f'Atention: file overwritten in {path}')
    except:
        raise Exception("Something went wrong when saving")
    
def dict_to_csv(path:str, obj:dict, rewrite:bool=False, verbose:bool=False):
    """Dumps dict into csv

    Parameters
    ----------
    path : str
        Path to pickle file
    obj : dict
        Dictionary to save as csv
    rewrite : bool, optional
        If already exists a file named as path it rewrites it, by default False
    verbose : bool, optional
        Whether to print information about rewritting, by default False

    Raises
    ------
    Exception
        If the file already exists and rewrite wasnt called.
    Exception
        Something went wrong.
    """
    isfile = os.path.isfile(path)
    if isfile and not rewrite:
        raise Exception("This file already exists, change 'rewrite=True'.")
    try:
        with open(path, 'w') as csv_file:  
            writer = csv.writer(csv_file, delimiter=':')
            for key, value in obj.items():
                writer.writerow([key, value])
        if isfile and verbose:
            print(f'Atention: file overwritten in {path}')
    except:
        raise Exception("Something went wrong when saving")

def all_possible_combinations(a:list):
    """Make a list with all possible combinations of the elements on a list

    Parameters
    ----------
    a : list
        The list of elements to be combined

    Returns
    -------
    list
        list of lists with all possible combinations of the elements of the list
    """
    if len(a) == 0:
        return [[]]
    cs = []
    for c in all_possible_combinations(a[1:]):
        cs += [c, c+[a[0]]]
    return cs

def stimuli_sequence(input_data:dict, number_of_trials:int, go_percentage:float, go_label:str, nogo_label:str):
    """Creates a stimuli sequence given a dictionary with words classified by binary categories (there should be as many groups as twice the number of categories), given it's labels.

    Parameters
    ----------
    input_data : dict
        Dictionary of words classified by categories
    number_of_trials : int
        Number of words presented in each stimuli sequence
    go_percentage : float
        Percentage (over the number of trials) that are used as "go" stimuli
    go_label : str
        Category used as "go"
    nogo_label : str
        Category used as "nogo"


    Returns
    -------
    list
        Shuffled sequence of words chose according to parameters passed
    """
    # Calculamos el número de samples que serán de tipo go
    number_of_go_samples = int((number_of_trials*go_percentage)/100)

    # Elegimos aleatoriamente tantas palabras como sean necesarias
    stimuli_sequence = np.random.choice(
                                    a=input_data[go_label], 
                                    size=number_of_go_samples,
                                    replace=False
                                        ).tolist()
    stimuli_sequence += np.random.choice(
                                    a=input_data[nogo_label], 
                                    size=number_of_trials-number_of_go_samples,
                                    replace=False
                                        ).tolist()
    # Los mezclamos 
    shuffle(stimuli_sequence)
    return stimuli_sequence

def routine(experiment_information:dict,
            input_data:dict, 
            go_label:str,
            nogo_label:str,
            win:psy.visual.window.Window,
            experiment_clock:psy.clock.Clock,# TODO LLENAR CLASE
            fixation:psy.visual.shape.ShapeStim, # TODO LLENAR CLASE
            fontsize:float=.15,
            ):
    # Este es el diccionario donde va a ir el output
    returned_data = {key: [] for key in ['trial','stimulus','answer','response_time(s)','cumulative_response_time(s)',\
                            'fixation_onset','fixation_duration','stimulus_onset','stimulus_duration',\
                            'response_duration', 'trial_duration']}

    # ============================================================================
    # Creamos los títulos de las instrucciones y los hiperparámetros de la corrida
    # El título
    # Una vez que presione la tecla comenzará el experimento
    get_ready_text = psy.visual.TextStim(
                                    win=win, 
                                    text='Presione la barra para continuar',
                                    height=fontsize,
                                    font='Arial',
                                    color='white',
                                    anchorHoriz='center',
                                    anchorVert='center',
                                    pos=(0.0,0.0)
                                    )

    # La secuencia de estímulos y los estímulos que aparecerán en cada trial
    stimuli_list = stimuli_sequence(
                                    input_data=input_data,
                                    number_of_trials=experiment_information['number_of_trials'],
                                    go_percentage=experiment_information['go_percentage'],
                                    go_label=go_label,
                                    nogo_label=nogo_label
                                    )
    stimuli = {trial:psy.visual.TextStim(win=win, text=stimulus, font='Arial', height=fontsize, anchorHoriz='center', anchorVert='center', pos=(.0,.0)
                                    ) for trial, stimulus in enumerate(stimuli_list)}
    stimuli={}
    for trial, stimulus in enumerate(stimuli_list):
        stimuli[trial] = psy.visual.TextStim(win=win, text=stimulus, font='Arial', height=fontsize, anchorHoriz='center', anchorVert='center', pos=(.0,.0))
    # Las instrucciones específicas de esta rutina
    instructions_text = psy.visual.TextStim(
                                    win=win,
                                    text=f'Presiona la barra espaciadora sólo si la palabra representa algo {go_label}',
                                    font='Arial',
                                    height=fontsize,
                                    color='white',
                                    anchorHoriz='center',
                                    anchorVert='center',
                                    pos=(0.0,0)
                                    )
    # ==================
    # Empieza la corrida

    # Mostramos la introducción
    instructions_text.draw()
    win.flip() 
    psy.event.waitKeys(keyList='space')

    # Ventana de inicialización
    get_ready_text.draw()
    win.flip()
    psy.event.waitKeys(keyList='space')

    # Reseteamos el reloj para guardar los tiempos del experimento
    experiment_clock.reset()

    # Inicializamos la duración del primer trial
    time_elapsed = 0

    # Iteramos sobre la secuencia de estímulos
    for trial, stimulus in enumerate(stimuli_list):
            
        # Definimos la duración del estímulo en frames
        stimulus_duration = int(random.gauss(mu=1, sigma=0.2)*experiment_information['frame_rate']) # entre .8 y 1.2 segs aprox
        
        # Definimos la duración que tiene el participante para responder
        response_duration = int(random.gauss(mu=1.5, sigma=0.2)*experiment_information['frame_rate']) # entre 1 y 2 segs 
        
        # El comienzo de la fijación en la cruz
        fixation_onset = time_elapsed
        
        # El comienzo del blanco antes del estímulo se fija con el fin de la fijación
        first_blank_onset = fixation_onset + experiment_information['fixation_number_of_frames']

        # El comienzo del primer estímulo será luego del primer blanco
        stimulus_onset = first_blank_onset + experiment_information['first_blank_number_of_frames']

        # Presentamos la cruz
        for s in range(experiment_information['fixation_number_of_frames']):
            fixation.draw()
            win.flip()
        
        # El primer blanco
        for p in range(experiment_information['first_blank_number_of_frames']):
            win.flip()
        
        # Borramos todos los eventos que ya hayan sucedido
        psy.event.clearEvents(eventType=None)

        # Inicializamos la respuesta como falsa
        already_responded = False

        # Empezamos el estímulo y el tiempo de respuesta
        start_response = experiment_clock.getTime()
        
        # Mientras pueda responder (entre 1 y 2s) mostramos el estímulo (entre 0.8 y 1.2 s)
        for frame in range(response_duration):
            if frame<stimulus_duration:
                stimuli[trial].draw()
                condition = 1 if stimulus in input_data[go_label] else 0
                win.flip()
            else: # cuando termina el estímulo sigue mostrando el blanco porque está dentro del tiempo para responder
                win.flip()
            
            # Si no respondió
            if not already_responded:
                # Obtenemos todos los eventos
                response = psy.event.getKeys(keyList='space', timeStamped=True)

                # Si la lista es mayor que cero, respondió
                if len(response) > 0:
                    already_responded = True
                    cumulative_response_time = round(experiment_clock.getTime(), 3)
                    response_time = round(experiment_clock.getTime() - start_response, 3)
                    answer = 1 if condition==1 else 0

                    # Llenamos el outputfile con la información de la respuesta
                    returned_data['trial'].append(trial)
                    returned_data['stimulus'].append(stimulus)
                    returned_data['answer'].append(answer)
                    returned_data['response_time(s)'].append(response_time)
                    returned_data['cumulative_response_time(s)'].append(cumulative_response_time)
                    returned_data['fixation_onset'].append(fixation_onset)
                    returned_data['fixation_duration'].append(experiment_information['fixation_number_of_frames'])
                    returned_data['stimulus_onset'].append(stimulus_onset)
                    returned_data['stimulus_duration'].append(stimulus_duration)
                    returned_data['response_duration'].append(response_duration)

                    # Debería salir, porque ya respondió no? # TODO ESTO NO ESTÁ
                    # break

        # Si terminó el estímulo y no respondió
        if not already_responded:
            answer = 1 if condition==0 else 0
            
            # Llenamos el outputfile con la información de la respuesta
            returned_data['trial'].append(trial)
            returned_data['stimulus'].append(stimulus)
            returned_data['answer'].append(answer)
            returned_data['response_time(s)'].append(np.nan)
            returned_data['cumulative_response_time(s)'].append(np.nan)
            returned_data['fixation_onset'].append(fixation_onset)
            returned_data['fixation_duration'].append(experiment_information['fixation_number_of_frames'])
            returned_data['stimulus_onset'].append(stimulus_onset)
            returned_data['stimulus_duration'].append(stimulus_duration)
            returned_data['response_duration'].append(response_duration)

        # Update de la duración del trial en frames (ESTO NO ESTABA)
        trial_duration =  response_duration + experiment_information['fixation_number_of_frames'] + experiment_information['first_blank_number_of_frames']
        returned_data['trial_duration'].append(trial_duration)

        # Update time elapsed in frames    
        time_elapsed += trial_duration
        return returned_data 