import os, random, numpy as np, pandas as pd
from time import strftime
from random import  randrange, shuffle

# Graphical user interface, visual-related objects, basic functions (timing, quit, etc.), input handler
from psychopy import  gui, visual, core, event

# Funciones auxiliares
from auxiliary import dump_pickle, dict_to_csv, load_pickle

# Cargamos las palabras de input del experimento
palabras = load_pickle(path='practica_1/input_experimento_1/palabras.pkl')

# ================================================================================================================================================
# Definimos los parámetros del experimento: se abre un diálogo en el cual se especifícan ID del sujeto, número de experimentos, porcentaje de go's
# ================================================================================================================================================
dialogue = gui.Dlg(title='Experiment Parameters')
dialogue.addText(text='Subejct information')
dialogue.addField('subject_id', label='Subject ID:*', initial=1)
dialogue.addField('name', label='Full name (using caps):*', initial='Max Power')
dialogue.addField('sex', label='Sex:*', choices=['M', 'F', 'NB', 'Rather not answer'])
dialogue.addField('age', label='Age:*')

dialogue.addText(text='Set-up experimental')
dialogue.addText(text='The sequence of each trial is: fixation, blank, stimulus, blank, answer')

dialogue.addField('number_of_trials', label='Número de trials (default, 30):', initial=30)
dialogue.addField('go_percentage', label='Porcentaje gos (default, 20):', initial=20)
dialogue.addField('experimenter', label='Experimenter full name (using caps; default, Juan Octavio Castro):*', initial='Juan Octavio Castro')
dialogue.addField('frame_rate', label='Frame rate of system (default, 60 Hz)', initial=60)
dialogue.addField('fixation_number_of_frames', label='Fixation number of frames before stimulus (default, 12):*', initial=12)
dialogue.addField('first_blank_number_of_frames', label='Blank number of frames previous to the stimulus (default, 3):*', initial=3)
dialogue.addField('response_key', label='Response key (default, space)', initial='space')

# Se abre la ventana de diálogo con todas los campos que especificamos más arriba. El objeto que se guarda es un diccionario con toda la información
experiment_information = dialogue.show()

# Ni idea que hace esto
# random.shuffle(experiment_information['pause_duration_in_frames'])

# Creamos el archivo donde vamos a guardar los datos
output_file_path = f"numTrials_{experiment_information['number_of_trials']}_goPctage_{int(experiment_information['go_percentage'])}"
output_file_path+= f"_participante_{experiment_information['subject_id']}_{strftime('%d-%m-%Y_%H-%M-%S')}.csv"
output_file_path = os.path.normpath(os.path.join(
                                                os.getcwd() + os.path.normpath('/practica_1/output_gonogo/'), 
                                                os.path.normpath(output_file_path)
                                                )
                                    )


# Guardamos un pkl con la información del setup
dump_pickle(path=output_file_path.replace('.csv', '.pkl'), obj=experiment_information, rewrite=True, verbose=True)

# Abrimos el archivo y ponemos el header
# output_file = open(output_file_path,'w+') # Suma por linea
# output_file.write('subject_id,number_of_trials,stim,correct,response_time,cumulative_response_time,fixation_onset,fixation_dur,stimulus_onset,stimulus_duration\n')
# output_file.flush() # limpia el buffer poniendo todo lo que queda colgado en el archivo
out = {key: [] for key in ['trial','stimulus','answer','response_time(s)','cumulative_response_time(s)',\
                                   'fixation_onset','fixation_duration','stimulus_onset','stimulus_duration',\
                                   'check_response_onset', 'response_duration', 'trial_duration']}
output_file = {'training':out, 'test':out}
# ===========================
# Configuramos el experimento
# ===========================

# Configuramos la tecla de salida del programa
event.globalKeys.clear()
def quit_experiment():
	core.quit()
event.globalKeys.add(key='q', func=quit_experiment)

# Creamos la secuencia de estímulos (go_percentage del numero de trials será entre 1 y 5, el resto entre 6 y 9)
def stimuli_sequence(input_data:dict, number_of_trials:int, go_percentage:float, go_label:str='grandes', nogo_label:str='chicas'):
        
    go_samples = int((number_of_trials*go_percentage)/100)
    stimuli_sequence = np.random.choice(
                                    a=input_data[go_label], 
                                    size=go_samples,
                                    replace=False
                                        ).tolist()
    stimuli_sequence += np.random.choice(
                                    a=input_data[nogo_label], 
                                    size=number_of_trials-go_samples,
                                    replace=False
                                        ).tolist()
    # Los mezclamos 
    shuffle(stimuli_sequence)
    return stimuli_sequence
stimuli_sequence_training = stimuli_sequence(
    input_data=palabras,
    number_of_trials=experiment_information['number_of_trials'],
    go_percentage=experiment_information['go_percentage']
    )
stimuli_sequence_test = stimuli_sequence(
    input_data=palabras,
    number_of_trials=experiment_information['number_of_trials'],
    go_percentage=experiment_information['go_percentage'],
    go_label='chicas',
    nogo_label='grandes'
    )

# Inicializamos la pantalla (va a aparecer)
win = visual.Window(
                    size=[683, 384], # seteando el tamaño en pixeles
                    color=[-1,-1,-1], # rgb, siendo cada uno en el rango -1,1
                    screen=1, # la pantalla física en la cual saldrá el experimento
                    fullscr=False, 
                    allowGUI=None, # si mostrar botones de cerrado e interacción en la pantalla
                    checkTiming=True, # si calcula el frame rate
                    allowStencil=True # permite poner en el buffer funciones del OpenGL
                    )

# Que no se visualice el mouse y tamaño de la letra
win.setMouseVisible(False)
fontsize = 0.15

# Crea la textura de la fijación
fixation = visual.shape.ShapeStim(
                                win=win, 
                                name='polygon', 
                                vertices='cross',
                                size=(0.05, 0.05),
                                ori=0, 
                                pos=(0, 0),
                                fillColor=[1,1,1], 
                                fillColorSpace='rgb',
                                lineColor=[-1,-1,-1],
                                opacity=1, 
                                depth=0.0, 
                                interpolate=True
                                )

# ===========================
# Mostramos las instrucciones
# ===========================

# El título
instructions_header = visual.TextStim(
                                    win=win, 
                                    text='INSTRUCCIONES', 
                                    font='Arial', 
                                    color='white', 
                                    anchorHoriz='center', 
                                    pos=(0.0,.8)
                                    )

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

# Una vez que presione la tecla comenzará el experimento
get_ready_text = visual.TextStim(
                                win=win, 
                                text='Vamos a comenzar. Presione la barra (...)',
                                height=fontsize,
                                font='Arial',
                                color='white',
                                anchorHoriz='center',
                                anchorVert='center',
                                pos=(0.0,0.0)
                                )

# Una vez que presione la tecla comenzará el experimento
get_ready_text = visual.TextStim(
                                win=win, 
                                text='Vamos a comenzar. Presione la barra (...)',
                                height=fontsize,
                                font='Arial',
                                color='white',
                                anchorHoriz='center',
                                anchorVert='center',
                                pos=(0.0,0.0)
                                )

# ==============================
# Creamos los estímulos visuales
# ==============================

# Hacemos el estímulo de cada posible valor
stimuli_training, stimuli_test = {}, {}
for trial, stimulus in enumerate(stimuli_sequence_training):
    stimuli_training[trial] = visual.TextStim(
                                win=win,
                                text=str(stimulus),
                                font='Arial',
                                height=fontsize,
                                anchorHoriz='center',
                                anchorVert='center',
                                pos=(.0,.0)
                                )
for trial, stimulus in enumerate(stimuli_sequence_test):
    stimuli_test[trial] = visual.TextStim(
                                win=win,
                                text=str(stimulus),
                                font='Arial',
                                height=fontsize,
                                anchorHoriz='center',
                                anchorVert='center',
                                pos=(.0,.0)
                                )
pause_text = visual.TextStim(
                            win=win, 
                            text='Terminaste el experimento',
                            color='white', 
                            anchorHoriz='center', 
                            anchorVert='center', 
                            pos=(0.0,0.0)
                            )

# ================================================
# Realizamos la rutina principal del entrenamiento
# ================================================

# Inicializamos el reloj 
experiment_clock = core.Clock()

# Mostramos la introducción
instructions_header.draw()
instructions_text_training.draw()
win.flip() # flip the front and back buffers after drawing everything for your frame
event.waitKeys(keyList='space')

# Ventana de inicialización
get_ready_text.draw()
win.flip()
event.waitKeys(keyList='space')

# Reseteamos el reloj para guardar los tiempos del experimento
win.flip()
experiment_clock.reset()

# Inicializamos la duración del primer trial
time_elapsed = 0

# Iteramos sobre la secuencia de estímulos
for trial, stimulus in enumerate(stimuli_sequence_training):
        
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
    event.clearEvents(eventType=None)

    # Inicializamos la respuesta como falsa
    already_responded = False

    # Empezamos el estímulo y el tiempo de respuesta
    start_stimulus = experiment_clock.getTime()
    start_response = experiment_clock.getTime()
    
    # Mientras pueda responder (entre 1 y 2s) mostramos el estímulo (entre 0.8 y 1.2 s)
    for frame in range(response_duration):
        if frame<stimulus_duration:
            stimuli_training[trial].draw()
            condition = 1 if stimulus in palabras['grandes'] else 0
            win.flip()
        else: # cuando termina el estímulo sigue mostrando el blanco porque está dentro del tiempo para responder
            win.flip()
        
        # Si no respondió
        if not already_responded:
            # Obtenemos todos los eventos
            response = event.getKeys(keyList='space', timeStamped=True)

            # Si la lista es mayor que cero, respondió
            if len(response) > 0:
                already_responded = True
                cumulative_response_time = round(experiment_clock.getTime(), 3)
                response_time = round(experiment_clock.getTime() - start_response, 3)
                answer = 1 if condition==1 else 0

                # Llenamos el outputfile con la información de la respuesta
                output_file['training']['trial'].append(trial)
                output_file['training']['stimulus'].append(stimulus)
                output_file['training']['answer'].append(answer)
                output_file['training']['response_time(s)'].append(response_time)
                output_file['training']['cumulative_response_time(s)'].append(cumulative_response_time)
                output_file['training']['fixation_onset'].append(fixation_onset)
                output_file['training']['fixation_duration'].append(experiment_information['fixation_number_of_frames'])
                output_file['training']['stimulus_onset'].append(stimulus_onset)
                output_file['training']['stimulus_duration'].append(stimulus_duration)
                output_file['training']['response_duration'].append(response_duration)

                # Debería salir, porque ya respondió no? # TODO ESTO NO ESTÁ
                # break

    # Si terminó el estímulo y no respondió
    if not already_responded:
        answer = 1 if condition==0 else 0
        
        # Llenamos el outputfile con la información de la respuesta
        output_file['training']['trial'].append(trial)
        output_file['training']['stimulus'].append(stimulus)
        output_file['training']['answer'].append(answer)
        output_file['training']['response_time(s)'].append(np.nan)
        output_file['training']['cumulative_response_time(s)'].append(np.nan)
        output_file['training']['fixation_onset'].append(fixation_onset)
        output_file['training']['fixation_duration'].append(experiment_information['fixation_number_of_frames'])
        output_file['training']['stimulus_onset'].append(stimulus_onset)
        output_file['training']['stimulus_duration'].append(stimulus_duration)
        output_file['training']['response_duration'].append(response_duration)

    # Update de la duración del trial en frames (ESTO NO ESTABA)
    trial_duration =  response_duration + experiment_information['fixation_number_of_frames'] + experiment_information['first_blank_number_of_frames']
    output_file['training']['trial_duration'].append(trial_duration)

    # Update time elapsed in frames    
    time_elapsed += trial_duration


instructions_text_middle.draw()
win.flip()
event.waitKeys(keyList='space')
# =========================================
# Realizamos la rutina principal del testeo
# =========================================

# Mostramos la introducción
instructions_header.draw()
instructions_text_test.draw()
win.flip() # flip the front and back buffers after drawing everything for your frame
event.waitKeys(keyList='space')

# Ventana de inicialización
get_ready_text.draw()
win.flip()
event.waitKeys(keyList='space')

# Reseteamos el reloj para guardar los tiempos del experimento
win.flip()
experiment_clock.reset()

# Inicializamos la duración del primer trial
time_elapsed = 0

# Iteramos sobre la secuencia de estímulos
for trial, stimulus in enumerate(stimuli_sequence_test):
        
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
    event.clearEvents(eventType=None)

    # Inicializamos la respuesta como falsa
    already_responded = False

    # Empezamos el estímulo y el tiempo de respuesta
    start_stimulus = experiment_clock.getTime()
    start_response = experiment_clock.getTime()
    
    # Mientras pueda responder (entre 1 y 2s) mostramos el estímulo (entre 0.8 y 1.2 s)
    for frame in range(response_duration):
        if frame<stimulus_duration:
            stimuli_test[trial].draw()
            condition = 1 if stimulus in palabras['chicas'] else 0
            win.flip()
        else: # cuando termina el estímulo sigue mostrando el blanco porque está dentro del tiempo para responder
            win.flip()
        
        # Si no respondió
        if not already_responded:
            # Obtenemos todos los eventos
            response = event.getKeys(keyList='space', timeStamped=True)

            # Si la lista es mayor que cero, respondió
            if len(response) > 0:
                already_responded = True
                cumulative_response_time = round(experiment_clock.getTime(), 3)
                response_time = round(experiment_clock.getTime() - start_response, 3)
                answer = 1 if condition==1 else 0

                # Llenamos el outputfile con la información de la respuesta
                output_file['test']['trial'].append(trial)
                output_file['test']['stimulus'].append(stimulus)
                output_file['test']['answer'].append(answer)
                output_file['test']['response_time(s)'].append(response_time)
                output_file['test']['cumulative_response_time(s)'].append(cumulative_response_time)
                output_file['test']['fixation_onset'].append(fixation_onset)
                output_file['test']['fixation_duration'].append(experiment_information['fixation_number_of_frames'])
                output_file['test']['stimulus_onset'].append(stimulus_onset)
                output_file['test']['stimulus_duration'].append(stimulus_duration)
                output_file['test']['response_duration'].append(response_duration)

                # Debería salir, porque ya respondió no? # TODO ESTO NO ESTÁ
                # break

    # Si terminó el estímulo y no respondió
    if not already_responded:
        answer = 1 if condition==0 else 0
        
        # Llenamos el outputfile con la información de la respuesta
        output_file['test']['trial'].append(trial)
        output_file['test']['stimulus'].append(stimulus)
        output_file['test']['answer'].append(answer)
        output_file['test']['response_time(s)'].append(np.nan)
        output_file['test']['cumulative_response_time(s)'].append(np.nan)
        output_file['test']['fixation_onset'].append(fixation_onset)
        output_file['test']['fixation_duration'].append(experiment_information['fixation_number_of_frames'])
        output_file['test']['stimulus_onset'].append(stimulus_onset)
        output_file['test']['stimulus_duration'].append(stimulus_duration)
        output_file['test']['response_duration'].append(response_duration)

    # Update de la duración del trial en frames (ESTO NO ESTABA)
    trial_duration =  response_duration + experiment_information['fixation_number_of_frames'] + experiment_information['first_blank_number_of_frames']
    output_file['test']['trial_duration'].append(trial_duration)

    # Update time elapsed in frames    
    time_elapsed += trial_duration
# Terminamos el experimento
pause_text.draw()
win.flip()
core.wait(secs=3)
win.close()

# Guardamos el output
output = pd.DataFrame(data=output_file, columns=output_file.keys())
output.columns