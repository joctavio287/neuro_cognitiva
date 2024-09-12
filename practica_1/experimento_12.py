import os, random, numpy as np
from time import strftime

# Graphical user interface, visual-related objects, basic functions (timing, quit, etc.), input handler
from psychopy import  gui, visual, core, event

# Funciones auxiliares
from practica_1.auxiliary import dump_pickle, load_pickle, all_possible_combinations, stimuli_sequence
# from auxiliary import dump_pickle, load_pickle, all_possible_combinations, stimuli_sequence

# Cargamos las palabras de input del experimento
palabras = load_pickle(path='practica_1/input_experimento_1/palabras_doble_categoria.pkl')

max_data = min([len(palabras[key]) for key in palabras])
palabras = {key:palabras[key][:max_data] for key in palabras}
categorias_posibles = [element for element in all_possible_combinations(a=list(palabras.keys())) if len(element)==2]
random.shuffle(categorias_posibles)

# ================================================================================================================================================
# Definimos los parámetros del experimento: se abre un diálogo en el cual se especifícan ID del sujeto, número de experimentos, porcentaje de go's
# ================================================================================================================================================
dialogue = gui.Dlg(title='Experiment Parameters')
dialogue.addText(text='Subejct information')
dialogue.addField('subject_id', label='Subject ID (The code is the first letter of experimenter name and then the number of the subject):*', initial='J0')
dialogue.addField('name', label='Full name (using caps):*', initial='Juan Octavio Castro')
dialogue.addField('sex', label='Sex:*', choices=['M', 'F', 'NB', 'Rather not answer'])
dialogue.addField('age', label='Age:*')


dialogue.addText(text='Set-up experimental')
dialogue.addText(text='The sequence of each trial is: fixation, blank, stimulus, blank, answer')
dialogue.addField('number_of_trials', label='Número de trials (default, 10. Max available, 32):', initial=30)
dialogue.addField('go_percentage', label='Porcentaje gos (default, 20):', initial=20)
dialogue.addField('experimenter', label='Experimenter full name (using caps; default, Juan Octavio Castro):*', initial='Juan Octavio Castro')
dialogue.addField('frame_rate', label='Frame rate of system (default, 60 Hz)', initial=60)
dialogue.addField('fixation_number_of_frames', label='Fixation number of frames before stimulus (default, 12):*', initial=12)
dialogue.addField('first_blank_number_of_frames', label='Blank number of frames previous to the stimulus (default, 3):*', initial=3)

# Se abre la ventana de diálogo con todas los campos que especificamos más arriba. El objeto que se guarda es un diccionario con toda la información
experiment_information = dialogue.show()
genre = 'listo' if experiment_information['sex']=='M' else 'lista' if experiment_information['sex']=='F' else 'listx'

# Creamos los archivos donde vamos a guardar los datos
file_date = strftime('%d-%m-%Y_%H-%M-%S')
output_file_path = f"output_participante_{experiment_information['subject_id']}_{file_date}.pkl"
output_file_path = os.path.normpath(os.path.join(
                                                os.getcwd() + os.path.normpath('/practica_1/output_experimento_1/'), 
                                                os.path.normpath(output_file_path)
                                                )
                                    )
metadata_path = os.path.normpath(os.path.join(
                                            os.getcwd() + os.path.normpath('/practica_1/output_experimento_1/'), 
                                            os.path.normpath(f"info_experimental_participante_{experiment_information['subject_id']}_{file_date}.pkl")
                                            )
                                    )
questionary_path = os.path.normpath(os.path.join(
                                            os.getcwd() + os.path.normpath('/practica_1/output_experimento_1/'), 
                                            os.path.normpath(f"questionary_participante_{experiment_information['subject_id']}_{file_date}.pkl")
                                            )
                                    )
# Creamos el output file: va a haber un diccionario out por cada categoría binaria. El experimento se repetirá en cada categoría
out = {key: [] for key in ['trial','stimulus','answer','response_time(s)','cumulative_response_time(s)',\
                            'fixation_onset','fixation_duration','stimulus_onset','stimulus_duration',\
                            'check_response_onset', 'response_duration', 'trial_duration']}

# Las categorías estarán ordenadas por tuplas de la pinta [go, nogo]
output_file = {tuple(key):{'train':out, 'test':out} for key in categorias_posibles}

# ===========================
# Configuramos el experimento
# ===========================

# Inicializamos la pantalla (va a aparecer)
win = visual.Window(
                    size=[683, 384], # seteando el tamaño en pixeles
                    color=[-1,-1,-1], # rgb, siendo cada uno en el rango -1,1
                    screen=1, # la pantalla física en la cual saldrá el experimento
                    fullscr=True, 
                    allowGUI=None, # si mostrar botones de cerrado e interacción en la pantalla
                    checkTiming=True, # si calcula el frame rate
                    allowStencil=True # permite poner en el buffer funciones del OpenGL
                    ) 

# # Configuramos la tecla de salida del programa #NO SOLO NO FUNCIONA SINO QUE ROMPE EL CODIGO
# event.globalKeys.clear()
# def quit_experiment(w):
#     w.close()
#     return
# event.globalKeys.add(key='q', func=quit_experiment, func_args=win)

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

# ======================================
# Creamos el título de las instrucciones
# ======================================

# Una vez que presione la tecla comenzará el experimento
presentation_text = visual.TextStim(
                                win=win, 
                                text='El experimento que estás por realizar dura cerca de 10 minutos, procurá estar en un lugar cómodo y tranquilo.\n\n Apretá la barra para continuar...',
                                height=fontsize,
                                font='Arial',
                                color='white',
                                anchorHoriz='center',
                                anchorVert='center',
                                pos=(0.0,0.0)
                                )

presentation_text_0 = visual.TextStim(
                                win=win, 
                                text='Vamos a comenzar. Para pasar entre pantallas apretá la barra espaciadora.',
                                height=fontsize,
                                font='Arial',
                                color='white',
                                anchorHoriz='center',
                                anchorVert='center',
                                pos=(0.0,0.0)
                                )
instructions_text_middle = visual.TextStim(
                                win=win, 
                                text='Vamos de nuevo ...',
                                height=fontsize,
                                font='Arial',
                                color='white',
                                anchorHoriz='center',
                                anchorVert='center',
                                pos=(0.0,0.0)
                                )
blank_text = visual.TextStim(
                            win=win, 
                            text='...',
                            height=fontsize,
                            font='Arial',
                            color='white',
                            anchorHoriz='center',
                            anchorVert='center',
                            pos=(0.0,0.0)
                            )

final_text = visual.TextStim(
                            win=win, 
                            text='¡¡Felicitaciones!!\n ¡Terminaste!',
                            height=fontsize,
                            font='Arial',
                            color='white',
                            anchorHoriz='center',
                            anchorVert='center',
                            pos=(0.0,0.0)
                            )

# ==============================
# Empezams las rutinas: la idea es iterar sobre las posibles combinaciones de categorías. Se tomarán dos corridas; en la primera se hará un experimento de gonogo y en la segunda se cambiará una categoría.
# ==============================

# Inicializamos el reloj 
experiment_clock = core.Clock()

# Mostramos la introducción
presentation_text_0.draw()
win.flip() # flip the front and back buffers after drawing everything for your frame
event.waitKeys(keyList='space')

# Ventana de inicialización
presentation_text.draw()
win.flip()
event.waitKeys(keyList='space')

# Reseteamos el reloj para guardar los tiempos del experimento
win.flip()
experiment_clock.reset()
for categories in output_file:
    #TRAIN
    go_label, nogo_label = categories[0], categories[1]

    # La secuencia de estímulos y los estímulos que aparecerán en cada trial
    stimuli_list = stimuli_sequence(
                                    input_data=palabras,
                                    number_of_trials=experiment_information['number_of_trials'],
                                    go_percentage=experiment_information['go_percentage'],
                                    go_label=go_label
                                    )
    stimuli = {trial:visual.TextStim(win=win, text=stimulus, font='Arial', height=fontsize, anchorHoriz='center', anchorVert='center', pos=(.0,.0), color='white'
                                    ) for trial, stimulus in enumerate(stimuli_list)}
    
    # Las instrucciones específicas de esta rutina
    instructions_text_1 = visual.TextStim(
                                    win=win,
                                    text='Presiona la barra espaciadora sólo si las palabras que vas a ver a continuación representan algo\n',
                                    font='Arial',
                                    height=fontsize,
                                    color='white',
                                    anchorHoriz='center',
                                    anchorVert='center',
                                    pos=(0.0,0.5)
                                    )
    
    subgolabel = go_label.split(' en relación con una persona promedio')[0].upper()
    
    # Las instrucciones específicas de esta rutina
    instructions_text_2 = visual.TextStim(
                                    win=win,
                                    text=f'{subgolabel}\n\n',
                                    font='Arial',
                                    height=fontsize,
                                    color='yellow',
                                    anchorHoriz='center',
                                    anchorVert='center',
                                    pos=(0.0,-0.1)
                                    )
    # Las instrucciones específicas de esta rutina
    instructions_text_3 = visual.TextStim(
                                    win=win,
                                    text=f'en relación con una persona promedio.\n\n Apreta la barra cuando estes {genre} para continuar',
                                    font='Arial',
                                    height=fontsize,
                                    color='white',
                                    anchorHoriz='center',
                                    anchorVert='center',
                                    pos=(0.0,-.45)
                                    )
    # ==================
    # Empieza la corrida

    # Mostramos la introducción
    instructions_text_1.draw()
    instructions_text_2.draw()
    instructions_text_3.draw()
    win.flip() 
    event.waitKeys(keyList='space')

    # # Ventana de inicialización
    # get_ready_text.draw()
    # win.flip()
    # event.waitKeys(keyList='space')

    # Reseteamos el reloj para guardar los tiempos del experimento
    experiment_clock.reset()

    # Inicializamos la duración del primer trial
    time_elapsed = 0

    # Iteramos sobre la secuencia de estímulos
    for trial, stimulus in enumerate(stimuli_list):
            
        # Definimos la duración del estímulo en frames
        stimulus_duration = int(random.gauss(mu=.6, sigma=0.2)*experiment_information['frame_rate']) # entre .6 y 1 segs aprox
        
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
        start_response = experiment_clock.getTime()
        
        # Mientras pueda responder (entre 1 y 2s) mostramos el estímulo (entre 0.8 y 1.2 s)
        for frame in range(response_duration):
            if frame<stimulus_duration:
                stimuli[trial].draw()
                condition = 1 if stimulus in palabras[go_label] else 0
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
                    output_file[categories]['train']['trial'].append(trial)
                    output_file[categories]['train']['stimulus'].append(stimulus)
                    output_file[categories]['train']['answer'].append(answer)
                    output_file[categories]['train']['response_time(s)'].append(response_time)
                    output_file[categories]['train']['cumulative_response_time(s)'].append(cumulative_response_time)
                    output_file[categories]['train']['fixation_onset'].append(fixation_onset)
                    output_file[categories]['train']['fixation_duration'].append(experiment_information['fixation_number_of_frames'])
                    output_file[categories]['train']['stimulus_onset'].append(stimulus_onset)
                    output_file[categories]['train']['stimulus_duration'].append(stimulus_duration)
                    output_file[categories]['train']['response_duration'].append(response_duration)

                    # Debería salir, porque ya respondió no? # TODO ESTO NO ESTÁ
                    # break

        # Si terminó el estímulo y no respondió
        if not already_responded:
            answer = 1 if condition==0 else 0
            
            # Llenamos el outputfile con la información de la respuesta
            output_file[categories]['train']['trial'].append(trial)
            output_file[categories]['train']['stimulus'].append(stimulus)
            output_file[categories]['train']['answer'].append(answer)
            output_file[categories]['train']['response_time(s)'].append(np.nan)
            output_file[categories]['train']['cumulative_response_time(s)'].append(np.nan)
            output_file[categories]['train']['fixation_onset'].append(fixation_onset)
            output_file[categories]['train']['fixation_duration'].append(experiment_information['fixation_number_of_frames'])
            output_file[categories]['train']['stimulus_onset'].append(stimulus_onset)
            output_file[categories]['train']['stimulus_duration'].append(stimulus_duration)
            output_file[categories]['train']['response_duration'].append(response_duration)

        # Update de la duración del trial en frames (ESTO NO ESTABA)
        trial_duration =  response_duration + experiment_information['fixation_number_of_frames'] + experiment_information['first_blank_number_of_frames']
        output_file[categories]['train']['trial_duration'].append(trial_duration)

        # Update time elapsed in frames    
        time_elapsed += trial_duration

    # Texto intermedio
    instructions_text_middle.draw()
    win.flip()
    event.waitKeys(keyList='space')

    #TEST
    go_label, nogo_label = categories[1], categories[0]
    
    # La secuencia de estímulos y los estímulos que aparecerán en cada trial
    stimuli_list = stimuli_sequence(
                                    input_data=palabras,
                                    number_of_trials=experiment_information['number_of_trials'],
                                    go_percentage=experiment_information['go_percentage'],
                                    go_label=go_label
                                    )
    stimuli = {trial:visual.TextStim(win=win, text=stimulus, font='Arial', height=fontsize, anchorHoriz='center', anchorVert='center', pos=(.0,.0), color='white'
                                    ) for trial, stimulus in enumerate(stimuli_list)}
    # Las instrucciones específicas de esta rutina
    instructions_text = visual.TextStim(
                                    win=win,
                                    text=f'Presiona la barra espaciadora sólo si las palabras que vas a ver a continuación representan algo {go_label}.\n\n Apreta la barra cuando estes {genre} para continuar',
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
    event.waitKeys(keyList='space')

    # # Ventana de inicialización
    # get_ready_text.draw()
    # win.flip()
    # event.waitKeys(keyList='space')

    # Reseteamos el reloj para guardar los tiempos del experimento
    experiment_clock.reset()

    # Inicializamos la duración del primer trial
    time_elapsed = 0

    # Iteramos sobre la secuencia de estímulos
    for trial, stimulus in enumerate(stimuli_list):
            
        # Definimos la duración del estímulo en frames
        stimulus_duration = int(random.gauss(mu=.6, sigma=0.2)*experiment_information['frame_rate']) # entre .6 y 1 segs aprox
        
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
        start_response = experiment_clock.getTime()
        
        # Mientras pueda responder (entre 1 y 2s) mostramos el estímulo (entre 0.8 y 1.2 s)
        for frame in range(response_duration):
            if frame<stimulus_duration:
                stimuli[trial].draw()
                condition = 1 if stimulus in palabras[go_label] else 0
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
                    output_file[categories]['test']['trial'].append(trial)
                    output_file[categories]['test']['stimulus'].append(stimulus)
                    output_file[categories]['test']['answer'].append(answer)
                    output_file[categories]['test']['response_time(s)'].append(response_time)
                    output_file[categories]['test']['cumulative_response_time(s)'].append(cumulative_response_time)
                    output_file[categories]['test']['fixation_onset'].append(fixation_onset)
                    output_file[categories]['test']['fixation_duration'].append(experiment_information['fixation_number_of_frames'])
                    output_file[categories]['test']['stimulus_onset'].append(stimulus_onset)
                    output_file[categories]['test']['stimulus_duration'].append(stimulus_duration)
                    output_file[categories]['test']['response_duration'].append(response_duration)

                    # Debería salir, porque ya respondió no? # TODO ESTO NO ESTÁ
                    # break

        # Si terminó el estímulo y no respondió
        if not already_responded:
            answer = 1 if condition==0 else 0
            
            # Llenamos el outputfile con la información de la respuesta
            output_file[categories]['test']['trial'].append(trial)
            output_file[categories]['test']['stimulus'].append(stimulus)
            output_file[categories]['test']['answer'].append(answer)
            output_file[categories]['test']['response_time(s)'].append(np.nan)
            output_file[categories]['test']['cumulative_response_time(s)'].append(np.nan)
            output_file[categories]['test']['fixation_onset'].append(fixation_onset)
            output_file[categories]['test']['fixation_duration'].append(experiment_information['fixation_number_of_frames'])
            output_file[categories]['test']['stimulus_onset'].append(stimulus_onset)
            output_file[categories]['test']['stimulus_duration'].append(stimulus_duration)
            output_file[categories]['test']['response_duration'].append(response_duration)

        # Update de la duración del trial en frames (ESTO NO ESTABA)
        trial_duration =  response_duration + experiment_information['fixation_number_of_frames'] + experiment_information['first_blank_number_of_frames']
        output_file[categories]['test']['trial_duration'].append(trial_duration)

        # Update time elapsed in frames    
        time_elapsed += trial_duration

# =========================
# Terminamos el experimento
# =========================
final_text.draw()
win.flip()
core.wait(secs=3)
win.close()


# Add questionary abput the experiment
final_dialogue, rate_scale = gui.Dlg(title='Experiment Parameters'), np.arange(1,11).tolist()
final_dialogue.addField(
                    'length_of_exp', 
                     label='¿Qué tan largo te pareció el experimento?*', 
                     choices=rate_scale
                    )
final_dialogue.addField(
                    'hability', 
                     label='¿Sentís que tu habilidad para resolver la tarea mejoraba o empeoraba conforme repetías el experimento?*',
                     choices=['mejoraba', 'empeoraba', 'no cambió']
                    )
final_dialogue.addField(
                    'hability_rate', 
                     label='Si tuvieras que cuantificar este cambio, ¿qué número le pondrías? (en caso de responder "no cambió" poner 0)', 
                     choices=[0]+rate_scale,
                     initial=0
                    )
final_dialogue.addField(
                    'comments', 
                     label='¡Cualquier comentario que quieras hacer nos sirve!', 
                     initial=''
                    )
questionary = final_dialogue.show()

# Guardamos el output
dump_pickle(path=output_file_path, obj=output_file, rewrite=True, verbose=True)

# Guardamos un pkl con la información del setup
dump_pickle(path=metadata_path, obj=experiment_information, rewrite=True, verbose=True)
dump_pickle(path=questionary_path, obj=questionary, rewrite=True, verbose=True)