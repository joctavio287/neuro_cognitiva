# Standard libraries 
import numpy as np, matplotlib.pyplot as plt, os
import matplotlib.pylab as pylab
params = {'legend.fontsize': 'x-large',
          'legend.title_fontsize': 'x-large',
          'figure.titlesize': 'xx-large',
          'axes.labelsize': 'x-large',
          'axes.titlesize':'x-large',
          'xtick.labelsize':'large',
          'ytick.labelsize':'large'}
pylab.rcParams.update(params)

# Modules
from auxiliary import dump_pickle, load_pickle

# Specific libraries
import mne

# raws_LRP = load_pickle(path='practica_2/input/raws_LRP.pkl')
# raws_ERN = load_pickle(path='practica_2/input/raws_ERN.pkl')
# epochs_LRP = load_pickle(path='practica_2/input/epochs_LRP.pkl')
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
        i, epochs
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

y1 = np.mean(avg_correct, 0)[ch_interest,:]
y2 = np.mean(avg_incorrect, 0)[ch_interest,:]
y1L = y1-(np.std(avg_correct,axis=0)/np.sqrt(avg_correct.shape[0])-1)[ch_interest,:]
y1H = y1+(np.std(avg_correct,axis=0)/np.sqrt(avg_correct.shape[0])-1)[ch_interest,:]
y2L = y2-(np.std(avg_incorrect,axis=0)/np.sqrt(avg_incorrect.shape[0])-1)[ch_interest,:]
y2H = y2+(np.std(avg_incorrect,axis=0)/np.sqrt(avg_incorrect.shape[0])-1)[ch_interest,:]

# plt.figure(tight_layout=True, figsize=(6,2))
# plt.plot(epochs.times*1e3, y1, c='b', label='Correct')
# plt.fill_between(epochs.times*1e3, y1L, y1H, color='b', alpha=0.4 )
# plt.plot(epochs.times*1e3, y2,c='orange',label='Incorrect')
# plt.fill_between(epochs.times*1e3, y2L, y2H, color='orange', alpha=0.4 )
# plt.xlabel('Tiempo (ms)')
# plt.ylabel(r'$\mu V$')
# plt.ylim(-10,15)
# plt.yticks([-10,-5,0,5,10,15])
# plt.grid(visible=True)
# plt.legend(title='FCz')
# plt.show(block=False)
# plt.savefig(os.path.join('practica_2/output/', 'corrects_incorrects.png'), dpi=800)


y = np.mean((avg_incorrect-avg_correct), axis=0)[ch_interest,:]
# deviation = np.sqrt((np.std(avg_incorrect,axis=0)/np.sqrt(avg_incorrect.shape[0]))**2+ (np.std(avg_incorrect,axis=0)/np.sqrt(avg_incorrect.shape[0]))**2)
deviation = np.std((avg_incorrect-avg_correct),axis=0)/np.sqrt((avg_incorrect-avg_correct).shape[0]-1)
yL = y - deviation[ch_interest,:]
yH = y + deviation[ch_interest,:]


# plt.figure(tight_layout=True, figsize=(5,2))
# plt.plot(epochs.times*1e3, y, c='g', label='Incorrect-Correct')
# plt.fill_between(epochs.times*1e3, yL, yH, color='g', alpha=0.4 )
# plt.xlabel('Tiempo (ms)', fontsize=12)
# plt.ylabel(r'$\mu V$', fontsize=12)
# plt.ylim(-18,12)
# plt.yticks([-18,-12,-6,0,6,12], fontsize=12)
# plt.xticks(fontsize=12)
# plt.grid(visible=True)
# plt.legend(title='FCz')
# plt.show(block=False)
# plt.savefig(os.path.join('practica_2/output/', 'ERN_ERP.png'), dpi=800)

freqs = np.array([4, 7, 8, 13]) 
data = avg_correct-avg_incorrect

out = mne.time_frequency.tfr_array_morlet(
                                        data=data,
                                        sfreq=256,
                                        freqs=freqs,
                                        n_cycles=2,
                                        decim=3
                                        )
data = (np.abs(out)).mean(axis=0)
inicial = epochs.times.tolist().index(-0.390625)
final = epochs.times.tolist().index(-0.19140625)

mean = np.mean(data[..., inicial:final], axis=-1, keepdims=True)
data /= mean
data = np.log10(data)

def get_axis_limits(ax, xscale=.7, yscale=.8):
    return ax.get_xlim()[1]*xscale, ax.get_ylim()[1]*yscale


fig = plt.figure(tight_layout=True,figsize=(12,4.5))
gs = fig.add_gridspec(2,2)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[1, 0])
ax3 = fig.add_subplot(gs[:, 1])

ax1.plot(epochs.times*1e3, y1, c='b', label='Correctas')
ax1.fill_between(epochs.times*1e3, y1L, y1H, color='b', alpha=0.4 )
ax1.plot(epochs.times*1e3, y2,c='orange',label='Incorrectas')
ax1.fill_between(epochs.times*1e3, y2L, y2H, color='orange', alpha=0.4 )
ax1.set(
        ylim=(-10,15), 
        # xlabel='Tiempo (ms)', 
        xticklabels=[],
        ylabel=r'$\mu V$',
        yticks=[-10,-5,0,5,10,15],
        )
ax1.annotate('(A)', xy=get_axis_limits(ax1), fontsize=12)
ax1.grid(visible=True)
ax1.legend()

ax2.plot(epochs.times*1e3, y, c='g', label='Incorrectas-Correctas')
ax2.fill_between(epochs.times*1e3, yL, yH, color='g', alpha=0.4 )
ax2.set(
        ylim=(-18,12), 
        ylabel=r'$\mu V$',
        xlabel='Tiempo (ms)', 
        # xticklabels=[],
        yticks=[-18,-12,-6,0,6,12,18],
        )
ax2.annotate('(B)', xy=get_axis_limits(ax2), fontsize=12)
ax2.grid(visible=True)
# ax2.legend(title='FCz')
ax2.legend()


im = ax3.pcolormesh(data[20], cmap='RdYlBu')#, vmin=data.min(), vmax=data.max())
ax3.set(
        xlabel='Tiempo (ms)', 
        ylabel='Bandas de frecuencia',
        xticks=np.linspace(0, 86.0, 6),
        xticklabels=[-600 , -400, -200, 0, 200, 400],
        yticks=[0.5,1.5,2.5,3.5],
        yticklabels=['Delta', 'Theta','7-8 Hz','Alpha']
        )
clb = plt.colorbar(im)
clb.set_label(label=r'$Log_{10}(\frac{Potencia}{Potencia_{promedio}})$')
# clb.ax.set_label(labelsize=15) # TODO CAMBIAR TAMAÑO DEL EJE DEL COLORBAR
ax3.annotate('(C)', xy=get_axis_limits(ax3,xscale=.01,yscale=.93), fontsize=12)
fig.show()
plt.savefig(os.path.join('practica_2/output/', 'fullpicture.png'), dpi=800)