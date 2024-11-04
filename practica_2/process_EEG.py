# Standard libraries 
import numpy as np, csv, datetime

# Specific libraries
from pipeline.datasets import get_erpcore
from mne.preprocessing import ICA
from mne.io import read_raw
from mne import set_bipolar_reference, Epochs, events_from_annotations, merge_events

# Modules
from auxiliary import dump_pickle, load_pickle

# Get data from experiment 
experiment_tagg = 'LRP' # N170, MMN, N2pc, N400, P3, ERN

# Get participants IDs
participants = []
with open(f'data/erpcore/{experiment_tagg}/participants.tsv') as fd:
    rd = csv.reader(fd, delimiter="\t", quotechar='"')
    for row in rd:
        # print(row)
        if row[0].startswith('sub'):
            participants.append(row[0])

# =================================================================================================================
# PREPROCESSING: create EOG channels, filter unwanted frequencies and occular artifacts, re-reference, segmentation
# =================================================================================================================
participants_raws_LRP = []
participants_epochs_LRP = []
participants_raws_ERN = []
participants_epochs_ERN = []

# Start preprocessing
start_time = datetime.datetime.now().replace(microsecond=0)

for j, participant in enumerate(participants):
    it_time = datetime.datetime.now().replace(microsecond=0)
    print(f'\n\n\t\t\t\tParticipant {j+1} out of {len(participants)}\n\n')

    # Loading
    files_dict = get_erpcore(component=experiment_tagg, participants=participant, path='data')

    # Load data into memory
    raw = read_raw(files_dict['raw_files'][0], preload=True, verbose=False)

    # Set EOG channels and drop them from original list of EEG channels
    raw = set_bipolar_reference(raw, anode='FP1', cathode='VEOG_lower', ch_name='VEOG', drop_refs=False, verbose=False)
    raw = set_bipolar_reference(raw, anode='HEOG_right', cathode='HEOG_left', ch_name='HEOG', drop_refs=False, verbose=False)
    raw = raw.set_channel_types({'VEOG': 'eog', 'HEOG': 'eog'})
    raw = raw.drop_channels(['VEOG_lower', 'HEOG_right', 'HEOG_left'])

    # Set montage specifying brande and type of headset, the match_case is to be case sensitive when calling them
    raw = raw.set_montage('biosemi64', match_case=False)

    # ====================================================
    # Filtering frequencies and artifacts and re-reference

    # Apply filter upto 40 Hz. Warning, very sensitive to what happen around 0 Hz, better to filter from 0.1 Hz instead
    raw = raw.filter(l_freq=0.1, h_freq=40) 

    # ======================================================================
    # Data segmentation TODO: this part depend on experiment, pending review
        
    # # See annotations on events
    # import json
    # with open(f'data/erpcore/{experiment_tagg}/task-{experiment_tagg}_events.json') as f:
    #     print(json.load(f))

    # ipsilateral = 111, 112, 211, 212
    # contralateral = 121, 122, 221, 222 

    # correct = 212, 222, 121, 111
    # incorrect = 112, 122, 221, 211

    # Get annotations
    events_LRP, event_id_LRP = events_from_annotations(raw) # events.shape # sample, duration, event tagg
    events_ERN, event_id_ERN = events_from_annotations(raw) # events.shape # sample, duration, event tagg

    events_LRP = merge_events(events_LRP, ids=np.array([2, 3, 8, 9]), new_id=1000)
    events_LRP = merge_events(events_LRP, ids=np.array([5, 6, 11, 12]), new_id=2000)
    events_ERN = merge_events(events_ERN, ids=np.array([9, 12, 5, 2]), new_id=3000)
    events_ERN = merge_events(events_ERN, ids=np.array([3, 6, 11, 8]), new_id=4000)
    event_id_LRP = {'Ipsilateral':1000, 'Contralateral':2000}
    event_id_ERN = {'Correct':3000, 'Incorrect':4000}

    
    # Resampling
    raw_aux = raw.copy()
    raw_LRP, events_LRP = raw.resample(sfreq=256, events=events_LRP)
    raw_ERN, events_ERN = raw_aux.resample(sfreq=256, events=events_ERN)
    
    # Remove occular artifats using independent component analysis (ICA) and plot mixing matrix of each component (weights given to each part of the surface on the scull)
    ica_LRP = ICA(n_components=15).fit(raw_LRP)
    ica_ERN = ICA(n_components=15).fit(raw_ERN)

    eog_indices_LRP, eog_scores_LRP = ica_LRP.find_bads_eog(
                                                            raw_LRP, ch_name=['HEOG', 'VEOG'],
                                                            verbose=False
                                                            )
    eog_indices_ERN, eog_scores_ERN = ica_ERN.find_bads_eog(
                                                            raw_ERN, ch_name=['HEOG', 'VEOG'],
                                                            verbose=False
                                                            )
    ica_LRP.exclude = eog_indices_LRP
    ica_ERN.exclude = eog_indices_ERN

    # Remove those components
    raw_LRP = ica_LRP.apply(raw_LRP)
    raw_ERN = ica_ERN.apply(raw_ERN)

    # Re-reference voltage offset
    raw_LRP = raw_LRP.set_eeg_reference(['P9','P10'])
    raw_ERN = raw_ERN.set_eeg_reference(['P9','P10'])
    
    # Make epochs (windows around event)
    epochs_LRP = Epochs(
                        raw_LRP, 
                        events_LRP, 
                        event_id_LRP, 
                        tmin=-0.8, #.8s before onset of events
                        tmax=0.2, #.2s after onset of events
                        baseline=(-.8,-.6) # use as baseline the previous
                        )

    epochs_ERN = Epochs(
                        raw_ERN, 
                        events_ERN, 
                        event_id_ERN, 
                        tmin=-0.6, #.6s before onset of events
                        tmax=0.4, #.4s after onset of events
                        baseline=(-.4,-.2) # use as baseline the previous
                        )

    # Filter bad channels. The criterion used is removing those channels with peak to peak voltage over 100 uV
    epochs_LRP = epochs_LRP.drop_bad({'eeg': 100e-6})
    epochs_ERN = epochs_ERN.drop_bad({'eeg': 100e-6})

    # Save pre_processed data-
    participants_raws_LRP.append(raw_LRP)
    participants_epochs_LRP.append(epochs_LRP)
    participants_raws_ERN.append(raw_ERN)
    participants_epochs_ERN.append(epochs_ERN)
    
    del raw, raw_ERN, raw_LRP, epochs_LRP, events_LRP, event_id_LRP, epochs_ERN, events_ERN, event_id_ERN
    print(datetime.datetime.now().replace(microsecond=0)- it_time)

# End preprocessing
end_time = (datetime.datetime.now().replace(microsecond=0)-start_time)
print(end_time)

dump_pickle(path='practica_2/input/raws_LRP.pkl', obj=participants_raws_LRP)
dump_pickle(path='practica_2/input/raws_ERN.pkl', obj=participants_raws_ERN)
dump_pickle(path='practica_2/input/epochs_LRP.pkl', obj=participants_epochs_LRP)
dump_pickle(path='practica_2/input/epochs_ERN.pkl', obj=participants_epochs_ERN)
