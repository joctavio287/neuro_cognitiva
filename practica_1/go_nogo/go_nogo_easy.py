# -*- coding: utf-8 -*-
from psychopy import  gui, visual, core, event
from time import strftime
from random import  randrange,shuffle
import numpy as np
import random

#%% Experimenter input
dlg = gui.Dlg(title = 'Experiment Parameters')
dlg.addText('Subejc info*')
dlg.addField('Subject ID:',initial='1')
dlg.addText('Número de trials*')
dlg.addField('# trials', initial='30')
dlg.addText('Porcentaje de "go"*')
dlg.addField('Porcentaje go:',initial='50')
id_inf = dlg.show()

exp_input = list(id_inf.values())

#%% Defino parametros
subid = exp_input[0]
ntrial = int(exp_input[1])
porc = float(exp_input[2])
fixation_dur = 12			# frames de fijación antes del estímulo
blank_dur_pre = 3
pause_dur = [258, 340]
blank_dur = 1
random.shuffle(pause_dur)

response_key = {'space'}     # Tecla de respuesta


#%% Output

### Results Logging ###
time_stamp = strftime('%d-%m-%Y_%H:%M:%S').replace(':','_') # Nombre del archivo
output_file_path = 'results/%s_%s_%s.csv'%(subid,ntrial,porc) #ubicación
output_file = open(output_file_path,'w+') # Suma por linea
output_file.write('subid,ntrial,estim,correct,response_time,cumulative_response_time,fixation_onset,fixation_dur,stim_onset,stim_dur\n') #Información que guarda
output_file.flush()

#%% Tecla de salida
event.globalKeys.clear()
quit_key = 'q'
def quit_experiment():
	core.quit()
event.globalKeys.add(key=quit_key, func=quit_experiment)


#%% Secuencia de estímulos
stim_sequence  = []
for n in range(ntrial):
    if n<ntrial*porc/100:
        stim_sequence.append(randrange(1,5,1))
    else:
        stim_sequence.append(randrange(6,9,1))
shuffle(stim_sequence)
print(stim_sequence)

#%% Inicializo pantalla

### Visuals ###
#window
win = visual.Window(size=[2880, 1800], color=[-1,-1,-1], screen = 0, fullscr = True, allowStencil = True)
win.setMouseVisible(False)
# aspect = float(win.size[1])/float(win.size[0]) #Rate de la pantalla
# print(aspect)
fontsize = 0.15


#%% Crea las texturas 
#Fijación
fixation = visual.ShapeStim(
				win=win, name='polygon', vertices='cross',
			    size=(0.05, 0.05),
			    ori=0, pos=(0, 0),
			    fillColor=[1,1,1], fillColorSpace='rgb',
				lineColor = [-1,-1,-1],
			    opacity=1, depth=0.0, interpolate=True)

#Instrucciones:
###texto
#headers
instructions_header = visual.TextStim(win, text='INSTRUCCIONES', 
                                      font = 'Arial', color = 'white', 
                                      anchorHoriz = 'center', pos=(0.0,.8))


#Main
instructions_text1 = visual.TextStim(win, text='Presiona la barra espaciadora sólo si el número es menor o igual a 5',
										font = 'Arial',
										height = fontsize,
										color = 'white',
										anchorHoriz = 'center',
										anchorVert = 'center',
										pos=(0.0,0))

get_ready_text = visual.TextStim(win, text='Vamos a comenzar. Presione la barra .... ',
										height = fontsize,
										font = 'Arial',
										color = 'white',
										anchorHoriz = 'center',
										anchorVert = 'center',
										pos=(0.0,0.0))


# Estimulos
est_1 = visual.TextStim(win, text='1',
                        font = 'Arial',
                        height = fontsize,
                        anchorHoriz = 'center',
                        anchorVert = 'center',
                        pos=(0.0,0.0))
est_2 = visual.TextStim(win, text='2',
                        font = 'Arial',
                        height = fontsize,
                        anchorHoriz = 'center',
                        anchorVert = 'center',
                        pos=(0.0,0.0))
est_3 = visual.TextStim(win, text='3',
                        font = 'Arial',
                        height = fontsize,
                        anchorHoriz = 'center',
                        anchorVert = 'center',
                        pos=(0.0,0.0))
est_4 = visual.TextStim(win, text='4',
                        font = 'Arial',
                        height = fontsize,
                        anchorHoriz = 'center',
                        anchorVert = 'center',
                        pos=(0.0,0.0))
est_5 = visual.TextStim(win, text='5',
                        font = 'Arial',
                        height = fontsize,
                        anchorHoriz = 'center',
                        anchorVert = 'center',
                        pos=(0.0,0.0))
est_6 = visual.TextStim(win, text='6',
                        font = 'Arial',
                        height = fontsize,
                        anchorHoriz = 'center',
                        anchorVert = 'center',
                        pos=(0.0,0.0))
est_7 = visual.TextStim(win, text='7',
                        font = 'Arial',
                        height = fontsize,
                        anchorHoriz = 'center',
                        anchorVert = 'center',
                        pos=(0.0,0.0))
est_8 = visual.TextStim(win, text='8',
                        font = 'Arial',
                        height = fontsize,
                        anchorHoriz = 'center',
                        anchorVert = 'center',
                        pos=(0.0,0.0))
est_9 = visual.TextStim(win, text='9',
                        font = 'Arial',
                        height = fontsize,
                        anchorHoriz = 'center',
                        anchorVert = 'center',
                        pos=(0.0,0.0))
pause_text = visual.TextStim(win, text='Fin', 
                             color = 'white', anchorHoriz = 'center', 
                             anchorVert = 'center', pos=(0.0,0.0))
#%% Inicializo tiempos 

# practice_clock = core.Clock()
experiment_clock = core.Clock()

#%% Rutina principal

###  instructions  ###
#explain task
#intro to experiment
instructions_header.draw()
instructions_text1.draw()
win.flip()
event.waitKeys(keyList='space')



get_ready_text.draw()
win.flip()
event.waitKeys(keyList='space')


## Main Experiment 

#clock reset
win.flip()
elapse_time = 0
last_trial_dur = 0
experiment_clock.reset()


elapse_time = 0
last_trial_dur = 0
for trial in range(ntrial):
    estimulo=stim_sequence[trial]
    stim_dur = int(random.gauss(1,0.2)*90) # Siempre en frames
    elapse_time += last_trial_dur
    response_dur = randrange(1,3)*90
    fixation_onset = elapse_time
    pre_blank_onset = fixation_onset + fixation_dur
    stim_onset = elapse_time + fixation_dur + blank_dur_pre
    blank_onset = elapse_time + fixation_dur + blank_dur_pre + stim_dur
    response_onset = elapse_time + fixation_dur + blank_dur_pre + stim_dur + blank_dur     
    for s in range(int(fixation_dur)):
        fixation.draw()
        win.flip()

    for p in range(int(blank_dur_pre)):
        win.flip()

    start_stimulus = experiment_clock.getTime()
    responded = False
    response = []
    event.clearEvents(eventType=None)
    start_response = experiment_clock.getTime()
    cond = 1
    for rr in range(int(response_dur)): # Grafica el estimulo
        if rr<int(stim_dur):
            if stim_sequence[trial]==1:
                est_1.draw()
            elif stim_sequence[trial]==2:
                est_2.draw()
            elif stim_sequence[trial]==3:
                est_3.draw()
            elif stim_sequence[trial]==4:
                est_4.draw()
            elif stim_sequence[trial]==5:
                est_5.draw()
            elif stim_sequence[trial]==6:
                est_6.draw()
                cond=0
            elif stim_sequence[trial]==7:
                est_7.draw()
                cond=0
            elif stim_sequence[trial]==8:
                est_8.draw()
                cond=0
            elif stim_sequence[trial]==9:
                est_9.draw()
                cond=0
            win.flip()
        else:
            win.flip()
        
    #response collection
        if not responded:
            response = event.getKeys(keyList='space', timeStamped=True)
            if len(response) > 0:
                responded = True
                cumulative_response_time = round(experiment_clock.getTime(),3)
                response_time = round(experiment_clock.getTime() - start_response,3)
                if cond==1:
                    correct = 1
                else:
                    correct = 0
                output_file.write(','.join([str(subid),str(trial+1),
                                         str(estimulo),str(correct),
                                         str(response_time),str(cumulative_response_time),
                                         str(fixation_onset),str(fixation_dur),
                                         str(stim_onset),str(stim_dur),
                                         str(response_onset),str(response_dur)+'\n']))
                output_file.flush()
                
    if not responded:
        if cond == 0:
            correct = 1
        else:
            correct = 0
        output_file.write(','.join([str(subid),str(trial+1),
                                    str(estimulo),str(correct),
                                    'NA','NA',
                                    str(fixation_onset),str(fixation_dur),
                                    str(stim_onset),str(stim_dur),
                                    str(response_onset),str(response_dur)+'\n']))
        output_file.flush()


pause_text.draw()
win.flip()
core.wait(3)
win.close()
		

