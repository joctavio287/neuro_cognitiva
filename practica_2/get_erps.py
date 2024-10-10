# Standard libraries 
import numpy as np, matplotlib.pyplot as plt

# Modules
from practica_2.auxiliary import dump_pickle, load_pickle

raws_LRP = load_pickle(path='practica_2/input/raws_LRP.pkl')
raws_ERN = load_pickle(path='practica_2/input/raws_ERN.pkl')
epochs_LRP = load_pickle(path='practica_2/input/epochs_LRP.pkl')
epochs_ERN = load_pickle(path='practica_2/input/epochs_ERN.pkl')

# Subjects 34, 35, 36 have no epochs. The rest have too little responses or non in one category
unwanted_subj_ERN = [2, 32, 33, 34, 35]
# Subjects 3, 33, 36 have no epochs. The rest have too little responses or non in one category
unwanted_subj_LRP = [2, 29, 32, 35]

correct = []
incorrect = []
for i, epochs in enumerate(epochs_ERN):
    # Filter unwanted subjects (those who dont have epochs)
    if i in unwanted_subj_ERN:
        continue

    # Group on epochs tagg taking average to get ERP
    evokeds_correct = epochs['Correct'].average()
    evokeds_correct.comment = 'Correct'
    evokeds_incorrect = epochs['Incorrect'].average()
    evokeds_incorrect.comment = 'Incorrect'

    # Compare ERPS
    correct.append(evokeds_correct.get_data()/1e-6)
    incorrect.append(evokeds_incorrect.get_data()/1e-6)

avg_correct = np.stack(correct)
avg_incorrect = np.stack(incorrect)

# ch_interest = raws_ERN[0].ch_names.index('FCz') # C3 es 4 C4 es 22 FCz es 20
ch_interest = 20

y1 = np.mean(avg_correct,0)[ch_interest,:]
y2 = np.mean(avg_incorrect,0)[ch_interest,:]
y1L = y1-(np.std(avg_correct,axis=0)/np.sqrt(avg_correct.shape[0])-1)[ch_interest,:]
y1H = y1+(np.std(avg_correct,axis=0)/np.sqrt(avg_correct.shape[0])-1)[ch_interest,:]
y2L = y2-(np.std(avg_incorrect,axis=0)/np.sqrt(avg_incorrect.shape[0])-1)[ch_interest,:]
y2H = y2+(np.std(avg_incorrect,axis=0)/np.sqrt(avg_incorrect.shape[0])-1)[ch_interest,:]

plt.figure(tight_layout=True, figsize=(6,2))
plt.plot(epochs.times*1e3, y1, c='b', label='Correct')
plt.fill_between(epochs.times*1e3, y1L, y1H, color='b', alpha=0.4 )
plt.plot(epochs.times*1e3, y2,c='orange',label='Incorrect')
plt.fill_between(epochs.times*1e3, y2L, y2H, color='orange', alpha=0.4 )
plt.xlabel('Tiempo (ms)')
plt.ylabel(r'$\mu V$')
plt.ylim(-10,15)
plt.yticks([-10,-5,0,5,10,15])
plt.grid(visible=True)
plt.legend(title='FCz')
plt.show(block=False)

y = np.mean((avg_incorrect-avg_correct), axis=0)[ch_interest,:]
# deviation = np.sqrt((np.std(avg_incorrect,axis=0)/np.sqrt(avg_incorrect.shape[0]))**2+ (np.std(avg_incorrect,axis=0)/np.sqrt(avg_incorrect.shape[0]))**2)
deviation = np.std((avg_incorrect-avg_correct),axis=0)/np.sqrt((avg_incorrect-avg_correct).shape[0]-1)
yL = y - deviation[ch_interest,:]
yH = y + deviation[ch_interest,:]


plt.figure(tight_layout=True, figsize=(6,2))
plt.plot(epochs.times*1e3, y, c='g', label='Incorrect-Correct')
plt.fill_between(epochs.times*1e3, yL, yH, color='g', alpha=0.4 )
plt.xlabel('Tiempo (ms)')
plt.ylabel(r'$\mu V$')
plt.ylim(-18,12)
plt.yticks([-18,-12,-6,0,6,12])
plt.grid(visible=True)
plt.legend(title='FCz')
plt.show(block=False)
plt.savefig(os.path.join('practica_1/output_experimento_1/imagenes', 'traintest.png'), dpi=600)