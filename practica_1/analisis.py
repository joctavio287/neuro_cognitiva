import os, numpy as np, pandas as pd, matplotlib.pyplot as plt, re, seaborn as sns
from scipy.stats import wilcoxon
import starbars

# Funciones auxiliares
from practica_1.auxiliary import dump_pickle, load_pickle
# from auxiliary import dump_pickle, load_pickle, all_possible_combinations, stimuli_sequence

# =========
# Read data
# Get the file names
info_files = [arch for arch in os.listdir('practica_1/output_experimento_1') if 'info_experimental' in arch]
output_files = [arch for arch in os.listdir('practica_1/output_experimento_1') if 'output_participante' in arch]

# Identify subjects that have performed the two parts of the experiment
subjects_with_bis = [re.search(pattern='([A-Z][0-9]+)', string=file).group() for file in info_files if file.endswith('bis.pkl')]
files, files_bis = {subj:{} for subj in subjects_with_bis},{subj:{} for subj in subjects_with_bis}

# Iterate over subjects and load dictionaries
for out_file in output_files:
    subj_id = re.search(pattern='([A-Z][0-9]+)', string=out_file).group()
    if subj_id in subjects_with_bis:
        if out_file.endswith('bis.pkl'):
            files_bis[subj_id] = load_pickle(path=os.path.join('practica_1/output_experimento_1/', out_file))
        else:
            files[subj_id] = load_pickle(path=os.path.join('practica_1/output_experimento_1/', out_file))

# Combine data to get one dictionary containing data from both experiments
data = {subj: files[subj]|files_bis[subj] for subj in files}

# =================================
# Split experiments into categories
# Iterate to get relevant data
results = {}
for subject in data:
    # Get experiments where size is the changed category between train and trial
    size = [stimulus for stimulus in data[subject].keys() if ('chico' in stimulus[0]) and ('grande' in stimulus[1])]
    size += [stimulus for stimulus in data[subject].keys() if ('grande' in stimulus[0]) and ('chico' in stimulus[1])]
    
    # Now get experiments where animated is the changed category between train and trial
    living = [stimulus for stimulus in data[subject].keys() if ('con vida' in stimulus[0]) and ('sin vida' in stimulus[1])]
    living += [stimulus for stimulus in data[subject].keys() if ('sin vida' in stimulus[0]) and ('con vida' in stimulus[1])]
    
    # Get experiments where both categories change at the same time and then exclude them from size and living
    size_living = [stimulus for stimulus in data[subject].keys() if (stimulus in living) and (stimulus in size)]
    living = [stimulus for stimulus in living if stimulus not in size_living]
    size = [stimulus for stimulus in size if stimulus not in size_living]

    # Analyze each type of experiment
    results[subject] = {'train':{
                                'living':{'response_time':[], 'answers':[]},
                                'size':{'response_time':[], 'answers':[]}, 
                                'size_living':{'response_time':[], 'answers':[]}
                                },
                        'test':{
                                'living':{'response_time':[], 'answers':[]},
                                'size':{'response_time':[], 'answers':[]}, 
                                'size_living':{'response_time':[], 'answers':[]}
                                }
                        }
    for experiment in living:
        results[subject]['train']['living']['response_time'] += data[subject][experiment]['train']['response_time(s)']
        results[subject]['test']['living']['response_time'] += data[subject][experiment]['test']['response_time(s)']
        results[subject]['train']['living']['answers'] += data[subject][experiment]['train']['answer']
        results[subject]['test']['living']['answers'] += data[subject][experiment]['test']['answer']
    results[subject]['train']['living']['response_time'] = np.array(results[subject]['train']['living']['response_time'])
    results[subject]['test']['living']['response_time'] = np.array(results[subject]['test']['living']['response_time'])
    results[subject]['train']['living']['answers'] = np.array(results[subject]['train']['living']['answers'])
    results[subject]['test']['living']['answers'] = np.array(results[subject]['test']['living']['answers'])
    for experiment in size:
        results[subject]['train']['size']['response_time'] += data[subject][experiment]['train']['response_time(s)']
        results[subject]['test']['size']['response_time'] += data[subject][experiment]['test']['response_time(s)']
        results[subject]['train']['size']['answers'] += data[subject][experiment]['train']['answer']
        results[subject]['test']['size']['answers'] += data[subject][experiment]['test']['answer']
    results[subject]['train']['size']['response_time'] = np.array(results[subject]['train']['size']['response_time'])
    results[subject]['test']['size']['response_time'] = np.array(results[subject]['test']['size']['response_time'])
    results[subject]['train']['size']['answers'] = np.array(results[subject]['train']['size']['answers'])
    results[subject]['test']['size']['answers'] = np.array(results[subject]['test']['size']['answers'])
    for experiment in size_living:
        results[subject]['train']['size_living']['response_time'] += data[subject][experiment]['train']['response_time(s)']
        results[subject]['test']['size_living']['response_time'] += data[subject][experiment]['test']['response_time(s)']
        results[subject]['train']['size_living']['answers'] += data[subject][experiment]['train']['answer']
        results[subject]['test']['size_living']['answers'] += data[subject][experiment]['test']['answer']
    results[subject]['train']['size_living']['response_time'] = np.array(results[subject]['train']['size_living']['response_time'])
    results[subject]['test']['size_living']['response_time'] = np.array(results[subject]['test']['size_living']['response_time'])
    results[subject]['train']['size_living']['answers'] = np.array(results[subject]['train']['size_living']['answers'])
    results[subject]['test']['size_living']['answers'] = np.array(results[subject]['test']['size_living']['answers'])

# ======================================
# Get relevant data in terms of subjects
# Averages across subjects    
def check_answer(answer:np.ndarray):
    # check number of correct answers
    true_answer = len(answer[answer==1])
    false_answer = len(answer[answer==0])
    return false_answer, true_answer

train_RT_living = []
train_RT_size = []
train_RT_size_living = []
test_RT_living = []
test_RT_size = []
test_RT_size_living = []

train_counts_living_correct = []
train_counts_living_incorrect = []
train_counts_size_correct = []
train_counts_size_incorrect = []
train_counts_size_living_correct = []
train_counts_size_living_incorrect = []
test_counts_living_correct = []
test_counts_living_incorrect = []
test_counts_size_correct = []
test_counts_size_incorrect = []
test_counts_size_living_correct = []
test_counts_size_living_incorrect = []

for subj in results:
    # Removing nans
    filter_liv = (~np.isnan(results[subj]['train']['living']['response_time'])&results[subj]['train']['living']['answers']==1)
    filter_siz = (~np.isnan(results[subj]['train']['size']['response_time'])&results[subj]['train']['size']['answers']==1)
    filter_siz_liv = (~np.isnan(results[subj]['train']['size_living']['response_time'])&results[subj]['train']['size_living']['answers']==1)
    train_RT_living.append(results[subj]['train']['living']['response_time'][filter_liv])
    train_RT_size.append(results[subj]['train']['size']['response_time'][filter_siz])
    train_RT_size_living.append(results[subj]['train']['size_living']['response_time'][filter_siz_liv])
    
    filter_liv = (~np.isnan(results[subj]['test']['living']['response_time'])&results[subj]['test']['living']['answers']==1)
    filter_siz = (~np.isnan(results[subj]['test']['size']['response_time'])&results[subj]['test']['size']['answers']==1)
    filter_siz_liv = (~np.isnan(results[subj]['test']['size_living']['response_time'])&results[subj]['test']['size_living']['answers']==1)
    test_RT_living.append(results[subj]['test']['living']['response_time'][filter_liv])
    test_RT_size.append(results[subj]['test']['size']['response_time'][filter_siz])
    test_RT_size_living.append(results[subj]['test']['size_living']['response_time'][filter_siz_liv])

    train_counts_living_correct.append(check_answer(answer=results[subj]['train']['living']['answers'])[1])
    train_counts_living_incorrect.append(check_answer(answer=results[subj]['train']['living']['answers'])[0])
    train_counts_size_correct.append(check_answer(answer=results[subj]['train']['size']['answers'])[1])
    train_counts_size_incorrect.append(check_answer(answer=results[subj]['train']['size']['answers'])[0])
    train_counts_size_living_correct.append(check_answer(answer=results[subj]['train']['size_living']['answers'])[1])
    train_counts_size_living_incorrect.append(check_answer(answer=results[subj]['train']['size_living']['answers'])[0])
    
    test_counts_living_correct.append(check_answer(answer=results[subj]['test']['living']['answers'])[1])
    test_counts_living_incorrect.append(check_answer(answer=results[subj]['test']['living']['answers'])[0])
    test_counts_size_correct.append(check_answer(answer=results[subj]['test']['size']['answers'])[1])
    test_counts_size_incorrect.append(check_answer(answer=results[subj]['test']['size']['answers'])[0])
    test_counts_size_living_correct.append(check_answer(answer=results[subj]['test']['size_living']['answers'])[1])
    test_counts_size_living_incorrect.append(check_answer(answer=results[subj]['test']['size_living']['answers'])[0])

#======================================================================================
# Violin plot to compare distribution of response time across categories and train/test
# Arange data according to train, test and category
total = len(train_counts_living_correct+train_counts_living_incorrect)

data = {
        'Categorías permutadas': ['Vida' for i in range(len(train_counts_living_incorrect))]+['Tamaño' for i in range(len(train_counts_living_incorrect))]+['Ambas' for i in range(len(train_counts_living_incorrect))],
        'Entrenamiento': (np.array(train_counts_living_correct)/total).tolist()+(np.array(train_counts_size_correct)/total).tolist()+(np.array(train_counts_size_living_correct)/total).tolist(),
        'Evaluación': (np.array(test_counts_living_correct)/total).tolist()+(np.array(test_counts_size_correct)/total).tolist()+(np.array(test_counts_size_living_correct)/total).tolist()
        }
# load into a dataframe and use melt to blend columns into rows (opposite of pivot, actually)
df = pd.DataFrame.from_dict(data)
pdf = df.melt(
            id_vars=['Categorías permutadas'], 
            value_vars=['Entrenamiento', 'Evaluación'], 
            var_name='Etapa', 
            value_name='Respuestas correctas [%]'
            )
# Re-scale to get percentages
pdf['Respuestas correctas [%]'] = pdf['Respuestas correctas [%]']*100

# Compute t-test for each category. Have to use wilcoxon test and not t test, because the distribution is not normal (in fact is non-parametric --i.e: it doesnt follow a known distribution)
test_results_size_living = wilcoxon(np.array(train_counts_size_living_correct)/total, np.array(test_counts_size_living_correct)/total)
test_results_living = wilcoxon(np.array(train_counts_living_correct)/total, np.array(test_counts_living_correct)/total)
test_results_size = wilcoxon(np.array(train_counts_size_correct)/total, np.array(test_counts_size_correct)/total)

# The Wilcoxon signed-rank test tests the null hypothesis that two related paired samples come from the same distribution. In particular, it tests whether the distribution of the differences x - y is symmetric about zero. It is a non-parametric version of the paired T-test.
# If pvalue<.5 we would reject the null hypothesis at a confidence level of 5%, concluding that there is a difference in height between the groups

# Make figure
plt.figure(tight_layout=True, figsize=(6,4))

# Use seaborn to create a violin plot where split=True, updating to percentage
ax = sns.violinplot(
                    data=pdf, 
                    x='Categorías permutadas', # qué va en el eje x
                    y='Respuestas correctas [%]', # qué va en el eje y
                    hue='Etapa', # en qué variable se hace el split de color
                    split=True, # If True shows the distribution just in one side
                    palette={'Entrenamiento':'C0', 'Evaluación':'C1'},
                    alpha=1
                    )
# Move the legend
sns.move_legend(ax, bbox_to_anchor=(.4, .15), loc='center left', frameon=False)

# Add annotations
annotations = [("Vida", "Vida", test_results_living.pvalue), ("Tamaño", "Tamaño", test_results_size.pvalue), ("Ambas", "Ambas", test_results_size_living.pvalue)]
starbars.draw_annotation(annotations=annotations, ax=ax, ns_show=False)

# Save figure
plt.show(block=False)
plt.savefig(os.path.join('practica_1/output_experimento_1/imagenes', 'traintest.png'), dpi=600)

#======================================================================================
# Violin plot to compare distribution of response time across categories and train/test
# Arange data according to train, test and category
# data = np.stack(((np.array(test_counts_living_correct)/total).tolist(),(np.array(test_counts_size_correct)/total).tolist(),(np.array(test_counts_size_living_correct)/total).tolist())).T
RT_s_l = np.array([arra.mean()*1e3 for arra in test_RT_size_living])
RT_l = np.array([arra.mean()*1e3 for arra in test_RT_living])
RT_s = np.array([arra.mean()*1e3 for arra in test_RT_size])
data = np.stack((RT_l, RT_s, RT_s_l)).T

df = pd.DataFrame(data=data, columns=['Vida', 'Tamaño', 'Ambas'])
df['Evaluación'] = ['' for i in range(data.shape[0])]

# Melt the dataframe to a long form
dfm = df.melt(
            id_vars='Evaluación', 
            var_name='Categorías permutadas',
            value_name='Tiempo de respuesta (ms)'
            )
dfm['Tiempo de respuesta (ms)'] = dfm['Tiempo de respuesta (ms)']

# Compute t-test across each possible combination of categories. 
test_living_vs_size = wilcoxon(np.array(test_counts_living_correct), np.array(test_counts_size_correct))
test_living_vs_size_living = wilcoxon(np.array(test_counts_living_correct), np.array(test_counts_size_living_correct))
test_size_vs_size_living = wilcoxon(np.array(test_counts_size_correct), np.array(test_counts_size_living_correct))

# Make figure
plt.figure(tight_layout=True, figsize=(6,4))

# Use seaborn to create a violin plot
ax = sns.violinplot(
                    data=dfm, 
                    x='Categorías permutadas', 
                    y='Tiempo de respuesta (ms)', 
                    hue='Categorías permutadas',
                    palette={'Vida':'C0', 'Tamaño':'C1', 'Ambas':'C2'},
                    alpha=1
                    )
# # Move the legend
# sns.move_legend(ax, bbox_to_anchor=(.4, .15), loc='center left', frameon=False)

# Add annotations
annotations = [("Vida", "Tamaño", round(test_living_vs_size.pvalue,3)), ("Vida", "Ambas", round(test_living_vs_size_living.pvalue,3)), ("Tamaño", "Ambas", round(test_size_vs_size_living.pvalue,3))]
starbars.draw_annotation(annotations=annotations, ax=ax, ns_show=True)

# Save figure
plt.show(block=False)
plt.savefig(os.path.join('practica_1/output_experimento_1/imagenes', 'categorias.png'), dpi=600)

# #=======================================================
# # tiempo de respuesta en función de trials por categoría
# trials_train = np.arange(30)
# trials_test = np.arange(30, 60)
# plt.figure(tight_layout=True)

# # Living
# for response_time_train,response_time_test in zip(train_RT_living,test_RT_living):
#     trial_train = np.arange(len(response_time_train))
#     trial_test = np.arange(trial_train[-1]+1, trial_train[-1]+1+len(response_time_test))
#     plt.plot(trial_train, response_time_train, marker='*', alpha=.5, color='green')#, label='V-Train')
#     plt.plot(trial_test, response_time_test, marker='*', alpha=1, color='green')#, label='V-Test')

# # Living
# for response_time_train,response_time_test in zip(train_RT_size, test_RT_size):
#     trial_train = np.arange(len(response_time_train))
#     trial_test = np.arange(trial_train[-1]+1, trial_train[-1]+1+len(response_time_test))
#     plt.plot(trial_train, response_time_train, marker='*', alpha=.5, color='red')#, label='V-Train')
#     plt.plot(trial_test, response_time_test, marker='*', alpha=1, color='red')#, label='V-Test')

# # Living
# for response_time_train,response_time_test in zip(train_RT_size_living, test_RT_size_living):
#     trial_train = np.arange(len(response_time_train))
#     trial_test = np.arange(trial_train[-1]+1, trial_train[-1]+1+len(response_time_test))
#     plt.plot(trial_train, response_time_train, marker='*', alpha=.5, color='blue')#, label='V-Train')
#     plt.plot(trial_test, response_time_test, marker='*', alpha=1, color='blue')#, label='V-Test')

# # for response_time in test_RT_living:
# #     trial_test = np.
# #     plt.plot(np.arange(len(response_time)), response_time, marker='*', alpha=1, color='green')#, label='V-Test')
# # # Size
# # plt.plot(trials_train, train_RT_size, fmt='.-', alpha=.5, color='red', label='T-Train')
# # plt.plot(trials_test, test_RT_size, fmt='.-', alpha=1, color='red', label='T-Test')
# # # Living
# # plt.plot(trials_train, train_RT_size_living, fmt='.-', alpha=.5, color='blue', label='A-Train')
# # plt.plot(trials_test, test_RT_size_living, fmt='.-', alpha=1, color='blue', label='A-Test')
# plt.xlabel('Número de trials')
# plt.ylabel('Tiempo de respuesta (s)')
# plt.grid(visible=True)
# plt.show(block=False)

# np.stack(train_RT_living, axis=0)

# # # los valores se repiten para todas las categorias, con tomar una sola es suficiente
# # # 'output_participante_J0_14-09-2024_21-41-15.pkl'
# # # 'output_participante_J3_12-09-2024_22-50-19.pkl'
# # # 'output_participante_J5_14-09-2024_20-26-12.pkl'
# # # 'output_participante_J9_13-09-2024_21-06-07.pkl'
# # # fili = ['output_participante_J0_14-09-2024_21-41-15.pkl','output_participante_J3_12-09-2024_22-50-19.pkl','output_participante_J5_14-09-2024_20-26-12.pkl','output_participante_J9_13-09-2024_21-06-07.pkl']
# # # for fail in fili:
# # #     indexes = [(i*30,(i+1)*30) for i in range(12)]
# # #     output = load_pickle(path=os.path.join('practica_1/output_experimento_1/', fail))
# # #     new_out = {key:{'train':{}, 'test':{}} for key in output}
# # #     llaves = [key for key in output]
# # #     for analysis in output[llaves[-1]]['test'].keys():
# # #         list_of_values = [[values for values in output[llaves[-1]]['test'][analysis][index_i:index_i1]] for index_i, index_i1 in indexes]
# # #         list_of_train = list_of_values[::2]
# # #         list_of_test = list_of_values[1::2]
# # #         for llave, value in zip(llaves, list_of_train):
# # #             new_out[llave]['train'][analysis]=value
# # #         for llave, value in zip(llaves, list_of_test):
# # #             new_out[llave]['test'][analysis]=value
# # #     dump_pickle(path=os.path.join('practica_1/output_experimento_1/', fail), obj=new_out, rewrite=True)


# questionary_files = [arch for arch in os.listdir('practica_1/output_experimento_1') if 'quest' in arch]
# for file in info_files:
    # subj_id = re.search(pattern='([A-Z][0-9]+)', string=file).group()
    # if subj_id in subjects_with_bis:
#         subj_id, load_pickle(path=os.path.join('practica_1/output_experimento_1/', file))['name']