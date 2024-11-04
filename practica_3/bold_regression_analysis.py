# Standard libraries
import pandas as pd, numpy as np, seaborn as sns, matplotlib.pyplot as plt, os, glob, warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from matplotlib.font_manager import FontProperties
from tqdm import tqdm
# fig = plt.figure(figsize=(5,1))
# plt.text(x=.15, y=.5,s='Mano derecha', size=25)
# ax=fig.gca()
# ax.axis('off')
# plt.savefig(os.path.join('practica_3/output',f'mano_d.png'), dpi=800)
# Specific libraries
from nilearn.plotting import view_img, plot_glass_brain, glass_brain, plot_anat, plot_epi, plot_stat_map
from bids import BIDSLayout, BIDSValidator
from nltools.data import Brain_Data, Design_Matrix
from nltools.stats import regress, zscore, find_spikes
from nltools.file_reader import onsets_to_dm
import nibabel as nib

# Load modules
import practica_3.functions_fmri as f_fmri

# To get data downlaod git-annex then go to desire folder and run (powershell)
# >> git clone https://gin.g-node.org/ljchang/Localizer

# don't remember if that was the url. Then to download incripted files 
# >> git annex get .
# to get all data. But if you want specific folders, run
# >> git annex get path/to/folder1 path/to/folder

# Create a layout
data_dir = 'C:/repos/Localizer/'
layout = BIDSLayout(data_dir, derivatives=True)

# Get layour of subject 1
layout.get(target='subject', scope='raw', suffix='T1w', return_type='file')[:10]
data = nib.load(layout.get(subject='S01', scope='raw', suffix='T1w',  extension='nii.gz')[0])
print(data.header, data.shape)

# Plot anatomic data
plot_anat(data)
plt.show()

# Plot amygdala with same anatomic data
amygdala_mask = Brain_Data(os.path.join(data_dir, 'FSL_BAmyg_thr0.nii.gz')).to_nifti()
view_img(amygdala_mask, data)
plt.show()

# PLot movements of the head while performing task
data = pd.read_csv(layout.get(subject='S01', scope='derivatives', extension='.tsv')[0].path, sep='\t')

fig, ax = plt.subplots(ncols=2, figsize=(15,5))
data.loc[:,['trans_x','trans_y','trans_z']].plot(ax=ax[0])
ax[0].set_ylabel('Translation (mm)', fontsize=16)
ax[0].set_xlabel('Time (TR)', fontsize=16)
ax[0].set_title('Translation', fontsize=18)

data.loc[:,['rot_x','rot_y','rot_z']].plot(ax=ax[1])
ax[1].set_ylabel('Rotation (radian)', fontsize=16)
ax[1].set_xlabel('Time (TR)', fontsize=16)
ax[1].set_title('Rotation', fontsize=18)
fig.show()

# La variable que creamos es de tipo "matriz de diseño". En "Column" tenemos el nombre de los distintos tipos de eventos, que se corresponden con las tareas o estimulaciones realizadas durante la adquisición.
dm = f_fmri.load_bids_events(layout, 'S01', 2.4)
dm.info()

# La ploteamos
fig, ax = plt.subplots(figsize=(20,3))
dm.plot(ax=ax)
fig.show()
dm.heatmap()
plt.show()

# Los regresores tienen que ser convolucionados por el HRF para modelar la señal de fMR
dm_conv = dm.convolve()
dm_conv.heatmap()
plt.show()

# Así transforma la HRF un regresor de la matriz de diseño
fig, ax = plt.subplots(figsize=(15,3))
dm_conv['horizontal_checkerboard_c0'].plot(ax=ax)
fig.show()

# Ahora la matriz de correlación, si hay correlación (colinealidad)entre las features no es bueno para el modelo
plt.figure(tight_layout=True)
sns.heatmap(dm_conv.corr(), vmin=-1, vmax=1, cmap='RdBu_r')
plt.show()

# Sumamos base de cosenos de baja frecuencia para capturar drifts que explican parte de la varianza que no tiene que ver con el modelo 
dm_conv_filt = dm_conv.add_dct_basis(duration=128)
dm_conv_filt.iloc[:,10:].plot()
plt.show()

# También un regresor constante (podríamos haber restado la media)
dm_conv_filt_poly = dm_conv_filt.add_poly()
dm_conv_filt_poly.heatmap()
plt.show()

#Sumamos polinomios de grado bajo (creo que es un poco redundante con los cosenos de baja frec, pero bueno)
dm_conv_filt_poly = dm_conv_filt.add_poly(order=2, include_lower=True)
dm_conv_filt_poly.heatmap()
plt.show()

# Agregamos también los efectos residuales de movimiento
covariates = pd.read_csv(layout.get(subject='S01', scope='derivatives', extension='.tsv')[0].path, sep='\t')
mc = covariates[['trans_x','trans_y','trans_z','rot_x', 'rot_y', 'rot_z']]

# Redefinimos la data 
data = Brain_Data(layout.get(subject='S01', task='localizer', scope='derivatives', suffix='bold', extension='nii.gz', return_type='file'))
plt.figure(figsize=(15,5))
plt.plot(zscore(mc))
plt.show()

# En forma de matriz queda (sumamos también las derivadas)
mc_cov = f_fmri.make_motion_covariates(mc, 2.4)
sns.heatmap(mc_cov)
plt.show()

# Si ploteamos podemos ver picos que se corresponden con movimientos muy repentinos de la cabeza
plt.figure(figsize=(15,3))
plt.plot(np.mean(data.data, axis=1), linewidth=3)
plt.xlabel('Time', fontsize=18)
plt.ylabel('Intensity', fontsize=18)
plt.show()

# Los identificamos
spikes = data.find_spikes(global_spike_cutoff=2.5, diff_spike_cutoff=2.5)

fig, ax = plt.subplots(figsize=(15,3))
spikes = Design_Matrix(spikes.iloc[:,1:], sampling_freq=1/2.4)
spikes.plot(ax=ax, linewidth=2)
fig.show()

# Ahora sí, sumamos todo
dm_conv_filt_poly_cov = pd.concat([dm_conv_filt_poly, mc_cov, spikes], axis=1)
dm_conv_filt_poly_cov.heatmap(cmap='RdBu_r', vmin=-1,vmax=1)
plt.show()

# Suavizamos la data para no perder la correlación espacial
smoothed = data.smooth(fwhm=6)
data.mean().plot()
plt.show()
smoothed.mean().plot()
plt.show()

# # Ahora sí, ajustamos el modelo
# smoothed.X = dm_conv_filt_poly_cov
# stats = smoothed.regress()

# # Los regresores
# print(smoothed.X.columns)

# #Promediamos los betas asociadas a las funciones motores
# c1 = np.zeros(len(stats['beta']))
# c1[[2,4,5,6]] = 1/4
# print(c1)
# motor = stats['beta'] * c1

# motor.iplot()
# plt.show()

# # Calculamos los betas para todos los sujetos
# layout = BIDSLayout(data_dir, derivatives=True)
# os.makedirs(os.path.join(data_dir, 'derivatives/betas'),exist_ok=True)
# spike_cutoff, fwhm, tr = 3, 6, 2.4
# for sub in tqdm(layout.get_subjects(scope='derivatives')):
#     data = Brain_Data(layout.get(subject=sub, scope='derivatives', suffix='bold', extension='nii.gz', return_type='file')[0])
#     data = data.smooth(fwhm=fwhm)
#     dm = f_fmri.load_bids_events(layout, sub, 2.4)
#     covariates = pd.read_csv(layout.get(subject=sub, scope='derivatives', extension='.tsv')[0].path, sep='\t')
#     mc_cov = f_fmri.make_motion_covariates(covariates[['trans_x','trans_y','trans_z','rot_x', 'rot_y', 'rot_z']], tr)
#     spikes = data.find_spikes(global_spike_cutoff=spike_cutoff, diff_spike_cutoff=spike_cutoff)
#     dm_cov = dm.convolve().add_dct_basis(duration=128).add_poly(order=1, include_lower=True)
#     dm_cov = dm_cov.append(mc_cov, axis=1).append(Design_Matrix(spikes.iloc[:, 1:], sampling_freq=1/tr), axis=1)
#     data.X = dm_cov
#     stats = data.regress()

#     # Write out all betas
#     stats['beta'].write(os.path.join(data_dir, f'derivatives/betas/{sub}_betas.nii.gz'))

#     # Write out separate beta for each condition
#     for i, name in enumerate([x[:-3] for x in dm_cov.columns[:10]]):

#         stats['beta'][i].write(os.path.join(data_dir, f'derivatives/betas/{sub}_beta_{name}.nii.gz'))

kind = 'video'
con1_name = f'{kind}_right_hand'
con1_file_list = glob.glob(os.path.join(data_dir, 'derivatives','betas', f'S*_{con1_name}*nii.gz'))
con1_file_list.sort()
con1_dat = Brain_Data(con1_file_list)
con1_stats = con1_dat.ttest()
print(con1_stats.keys())

con2_name = f'{kind}_left_hand'
con2_file_list = glob.glob(os.path.join(data_dir, 'derivatives','betas', f'S*_{con2_name}*nii.gz'))
con2_file_list.sort()
con2_dat = Brain_Data(con2_file_list)
con1_v_con2 = con1_dat-con2_dat
significance = .005
con1_v_con2_stats = con1_v_con2.ttest(permutation=True, threshold_dict={'unc':significance}) # p valor para el umbral


fig = plt.figure(figsize=(6, 2))  # Example: (10, 8) inches
fig.suptitle(r'Significancia estadística $\alpha=$'+f'{significance}')
nifti_img = con1_v_con2_stats['thr_t'].to_nifti()
im = plot_stat_map(
            nifti_img, 
            cut_coords=(-36,-18,54), 
            draw_cross=False,
            figure=fig,
            annotate=False,
            cmap='RdBu_r'
            )

# Access the colorbar and add a label
colorbar = im._cbar  # Access the colorbar object
colorbar.set_label("t-estadístico")

# Customize the font properties
font_properties = FontProperties(
                                family='DejaVu Sans',  # Font family (e.g., 'serif', 'sans-serif', 'monospace')
                                # style='italic',  # Font style ('normal', 'italic', or 'oblique')
                                # weight='bold',   # Font weight ('normal', 'bold', 'light', etc.)
                                size=12          # Font size
                                )

# Apply the font properties to the colorbar label
colorbar.ax.yaxis.label.set_font_properties(font_properties)
# colorbar.ax.set_aspect(1.5)  # Increase the 'aspect' value to make the colorbar thicker
# Manually adjust the colorbar position and size
colorbar.ax.set_position([0.93, 0.18, 0.025, 0.65])
# Adjust the figure layout
plt.subplots_adjust(top=0.9, bottom=0.2, left=0.1, right=0.9, hspace=0.5, wspace=0.5)
fig.show()
fig.savefig(os.path.join('practica_3/output',f'{kind}_coronal_sagital_axial_significant_activity.png'), dpi=800)

# Read the .tsv file into a DataFrame
file_path = os.path.join(data_dir, 'participants.tsv')
participants = pd.read_csv(file_path, sep='\t').head(28)
participants['age'].mean(), participants['age'].std(), participants['age'].min(), participants['age'].max()

np.unique(participants['sex'],return_counts=True)
# import statsmodels.stats.api as sms

# # Parameters
# n_subjects = 200 # Number of subjects
# alpha = 0.5     # Significance level

# effect_size = con1_v_con2_stats['t'].data/np.sqrt(n_subjects)

# # Calculate power
# power_analysis = sms.TTestIndPower()
# power = power_analysis.power(effect_size, n_subjects, alpha)
# print(f'Statistical power: {power:.2f}')