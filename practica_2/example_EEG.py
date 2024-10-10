# Standard libraries 
import numpy as np, matplotlib.pyplot as plt, pandas as pd, json

# Specific libraries
from pipeline.datasets import get_erpcore
from mne.viz import plot_compare_evokeds
from mne.preprocessing import ICA
from mne.io import read_raw
from mne import set_bipolar_reference, Epochs, events_from_annotations, merge_events

# Modules
# from auxiliary import read_csv

# Get data from experiment 
experiment_tagg = 'N170' # N170, MMN, N2pc, N400, P3, ERN
files_dict = get_erpcore('N170', participants='sub-004', path='data')

# =================================================================================================================
# PREPROCESSING: create EOG channels, filter unwanted frequencies and occular artifacts, re-reference, segmentation
# =================================================================================================================
# Loading

# Load data into memory
raw = read_raw(files_dict['raw_files'][0], preload=True)

# Get channel names to identify electrooculography channels
# raw.ch_names[:]

# Set EOG channels and drop them from original list of EEG channels
raw = set_bipolar_reference(raw, anode='FP1', cathode='VEOG_lower', ch_name='VEOG', drop_refs=False)
raw = set_bipolar_reference(raw, anode='HEOG_right', cathode='HEOG_left', ch_name='HEOG', drop_refs=False)
raw = raw.set_channel_types({'VEOG': 'eog', 'HEOG': 'eog'})
raw = raw.drop_channels(['VEOG_lower', 'HEOG_right', 'HEOG_left'])

# Set montage specifying brande and type of headset, the match_case is to be case sensitive when calling them
raw = raw.set_montage('biosemi64', match_case=False)

# Print information of data
raw.info

# # To visualize topographic disposition
# fig = raw.plot_sensors(
#                         kind='topomap', #topomap
#                         show_names=True,
#                         ch_type='eeg'
#                         ) 

# # Plot EEG to get a first look of the data
# fig = raw.plot(
#             start=60,
#             duration=5,
#             scalings={'eeg': 60e-6}
#             )

# # Compute and plot power spectral density
# power_spec = raw.compute_psd(
#                             fmin=0.1, 
#                             fmax=70,
#                             )
# fig = power_spec.plot()

# ====================================================
# Filtering frequencies and artifacts and re-reference

# Apply filter upto 40 Hz. Warning, very sensitive to what happen around 0 Hz, better to filter from 0.1 Hz instead
raw = raw.filter(l_freq=0.1, h_freq=40) 
# fig = raw.plot(
#                 start=60,
#                 duration=5,
#                 scalings={'eeg': 60e-6}
#                 )
# fig = raw.compute_psd(
#                     fmin=0, 
#                     fmax=70
#                     ).plot()

# Remove occular artifats using independent component analysis (ICA) and plot mixing matrix of each component (weights given to each part of the surface on the scull)
ica = ICA(n_components=15).fit(raw)
# fig = ica.plot_components()

eog_indices, eog_scores = ica.find_bads_eog(
                                            raw, ch_name=['HEOG', 'VEOG'],
                                            verbose=False
                                            )
ica.exclude = eog_indices

# # Note that indexes excluded are the ones with higher score in these plots
# fig_1 = ica.plot_scores(eog_scores[0], title='ICA component scores of HEOG')
# fig_2 = ica.plot_scores(eog_scores[1], title='ICA component scores of VEOG')

# Remove those components
raw = ica.apply(raw)

# Re-reference voltage offset
raw = raw.set_eeg_reference('average')
# fig = raw.plot(
#                 start=60.0, 
#                 duration=5.0
#                 # scalings={'eeg': 60e-6}
#                 )

# ======================================================================
# Data segmentation TODO: this part depend on experiment, pending review

# See annotations on events
with open('data/erpcore/N170/task-N170_events.json') as f:
    print(json.load(f))

# Get annotations
events, event_id = events_from_annotations(raw) # events.shape # sample, duration, event tagg

# The key is {'1-40': 'Stimulus - faces', '41-80': 'Stimulus - cars', '101-140': 'Stimulus - scrambled faces', '141-180': 'Stimulus - scrambled cars', '201': 'Response - correct', '202': 'Response - error'}
events = merge_events(events, ids=range(1, 41), new_id=1)
events = merge_events(events, ids=range(41, 81), new_id=2)
event_id = {'face': 1, 'car': 2}

# Make epochs (windows around event)
epochs = Epochs(
                raw, 
                events, 
                event_id, 
                tmin=-0.2, #.2s before onset of events
                tmax=0.8, #.8s after onset of events
                baseline=(-0.2,0) # use as baseline the previous .2s #This is polemic because these are consecutive stimuli, and that part may have relevant information
                )

# # Useful plot, recomend for understanding previous operation
# fig = epochs.plot(
#                 events=True,
#                 block=False, 
#                 event_id=True
#                 )

# Filter bad channels. The criterion used is removing those channels with peak to peak voltage over 100 uV
epochs = epochs.drop_bad({'eeg': 100e-6})

# Plot electrode potential across epochs
# fig = epochs.plot_image(picks='Pz')

# ===========================================
# PLot Evoked Related Potentials of each tagg

# Group on epochs tagg taking average to get ERP
evokeds_car = epochs['car'].average()
evokeds_car.comment = 'car'
evokeds_face = epochs['face'].average()
evokeds_face.comment = 'face'

# Compare ERPS
# faces = epochs['face'].get_data()/1e-6
# cars = epochs['car'].get_data()/1e-6
# ch_interest = raw.ch_names.index('Pz')

# # y1 = np.mean(faces,0)[ch_interest,:]
# # y2 = np.mean(cars,0)[ch_interest,:]
# # y1L = y1-np.std(faces,axis=0)/np.sqrt(faces.shape[0])
# # y1H = y1+np.std(faces,axis=0)/np.sqrt(faces.shape[0])
# # y2L = y2-np.std(cars,axis=0)/np.sqrt(cars.shape[0])
# # y2H = y2+np.std(cars,axis=0)/np.sqrt(cars.shape[0])

# # plt.figure(figsize=(6,4))
# # plt.plot(epochs.times, y1, c='b', label='Caras')
# # plt.fill_between(epochs.times, y1L[ch_interest,:], y1H[ch_interest,:], color='b', alpha=0.4 )
# # plt.plot(epochs.times,y2,c='orange',label='Autos')
# # plt.fill_between(epochs.times, y2L[ch_interest,:], y2H[ch_interest,:], color='orange', alpha=0.4 )
# # plt.xlabel('Tiempo (s)')
# # plt.ylabel(r'$\mu V$')
# # plt.grid(visible=True)
# # plt.legend()
# # plt.show(block=False)

# Time frequency analysis: compute time-frequency representation of each tagg
# # freqs = np.logspace(*np.log10([4, 30]), num=8)
freqs = np.array([4,6,8,12,18])
power_car, itc = epochs['car'].compute_tfr(
                                            method="morlet",
                                            freqs=freqs,
                                            n_cycles=2,
                                            average=True,
                                            return_itc=True,
                                            decim=3,
                                            )

power_face, itc = epochs['face'].compute_tfr(
                                            method="morlet", # parecido a transformada de fourier, pero en vez de convolusionar con un cuadrado lo hace con algo más suave (mayor amplitud en el centro)
                                            freqs=freqs, # es más rapida computacionalmente que una gaussiana. Fourier es cuadrada pq pesa todo por igual en cada ventana. El resultado de la convolucion es el peso que se le da a cada ventana
                                            n_cycles=2, # cuantos cicos entran en el wavelet de arriba
                                            average=True,
                                            return_itc=True,
                                            decim=3,
                                            )

# power_face.plot('Pz', baseline=(-0.2, 0), mode="logratio", vmin=-0.8, vmax=0.8, title='Cara')
# power_car.plot('Pz', baseline=(-0.2, 0), mode="logratio",  vmin=-0.8, vmax=0.8, title='Auto')

# # Plot band Theta
# ind_freq = np.where(power_car.freqs<8)[0]
# ind_t_base = np.where(power_car.times<0)[0][-1]
# ch_interest = raw.ch_names.index('Pz')

# base_car=np.mean(power_car.get_data()[ch_interest, ind_freq, :ind_t_base])
# base_face=np.mean(power_face.get_data()[ch_interest, ind_freq, :ind_t_base])

# Pz_power_car= np.mean(power_car.get_data()[ch_interest, ind_freq, :],axis=0)/base_car
# Pz_power_face= np.mean(power_face.get_data()[ch_interest, ind_freq, :],axis=0)/base_face

# fig=plt.figure(figsize=(6,4))
# plt.plot(power_car.times, Pz_power_car, c='orange', label='Autos')
# plt.plot(power_car.times, Pz_power_face, c='b', label='Caras')

# plt.xlabel('Tiempo (s)')
# plt.ylabel('a.u')
# plt.title('Theta en Pz' )
# plt.legend()
# plt.show()