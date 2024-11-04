import pickle, os, csv, numpy as np, random
from random import shuffle

# import psychopy as psy
from psychopy import visual, event, clock

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