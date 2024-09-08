import pickle, os, csv, numpy as np
from random import shuffle

from psychopy import  gui, visual, core, event

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

def routine(input_data:dict, 
            number_of_trials:int, 
            go_percentage:float, 
            go_label:str, 
            nogo_label:str,
            win:visual.window.Window,
            fontsize:float=.15): 

    # Creates the stimuli sequence    
    stimuli_sequence_training = stimuli_sequence(
                                                input_data=input_data,
                                                number_of_trials=number_of_trials,
                                                go_percentage=go_percentage,
                                                go_label=go_label,
                                                nogo_label=nogo_label
                                                )
    
    # Creamos la pantalla de instrucciones
    if 'chic' in go_label:
        go_instruction_text = f'Presiona la barra espaciadora sólo si la palabra que aparece en la pantalla representa algo chico'
        nogo_instruction_text = f'Presiona la barra espaciadora sólo si la palabra que aparece en la pantalla representa algo grande'
    else:
        go_instruction_text = f'Presiona la barra espaciadora sólo si la palabra que aparece en la pantalla representa algo grande'
        nogo_instruction_text = f'Presiona la barra espaciadora sólo si la palabra que aparece en la pantalla representa algo chico'
    if 'inani' in go_label:
        go_instruction_text += ' y sin vida.'
        nogo_instruction_text += ' y con vida.'
    else:
        go_instruction_text += ' y con vida.'
        nogo_instruction_text += ' y sin vida.'

    # Las instrucciones
    instructions_text_training = visual.TextStim(
                                        win=win,
                                        text='Presiona la barra espaciadora sólo si la palabra representa algo grande',
                                        font='Arial',
                                        height=fontsize,
                                        color='white',
                                        anchorHoriz='center',
                                        anchorVert='center',
                                        pos=(0.0,0)
                                        )

    instructions_text_middle = visual.TextStim(
                                        win=win,
                                        text='Vamos a repetir el experimento. Presiona la barra para continuar',
                                        font='Arial',
                                        height=fontsize,
                                        color='white',
                                        anchorHoriz='center',
                                        anchorVert='center',
                                        pos=(0.0,0)
                                        )

    instructions_text_test = visual.TextStim(
                                        win=win,
                                        text='Presiona la barra espaciadora sólo si la palabra representa algo chico',
                                        font='Arial',
                                        height=fontsize,
                                        color='white',
                                        anchorHoriz='center',
                                        anchorVert='center',
                                        pos=(0.0,0)
                                        )

