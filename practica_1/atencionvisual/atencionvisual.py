##The Posner Cuing task
#Synopsis of the study:
#-Present a probe to the left or right of fixation
#-Participants have to respond to the presence of the probe as quickly as possible
#-Precede the probe with a cue
#-Usually the cue predicts the probe location
#-We can measure the effect of attention by the difference in reaction times between correct and incorrect cues

#How do we even start?
#Don’t be tempted to try and write a script from beginning to end in one go! 
#Break it down into chunks that you can manage. e.g.:create a trial; create window; create fixation, cue and probe stimuli
#set up the timing of the trial
#set up conditions 
#need to alter probe location
#need to alter cues
#make sure data are being saved

#####################################################################################3
# Import libraries
from psychopy import visual, event, core, data, gui
import random, os

#%% Experimenter input
dlg = gui.Dlg(title = 'Experiment Parameters')
dlg.addText('Subejc info*')
dlg.addField('Subject ID:',initial='1')
id_inf = dlg.show()
exp_input = list(id_inf.values())

#%%  Defino parametros
info = {} #a dictionary
#present dialog to collect info
info['participant'] = exp_input[0]
#add additional info after the dialog has gone
info['fixTime'] = 1 # sec
info['cueTime'] = 0.1 # sec
info['probeTime'] = 0.2 # sec
info['dateStr'] = data.getDateStr() #will create str of current date/time
frs = 90
response_key = {'left','right'}     # Tecla de respuesta

#%% Datos de salida
filename = os.path.join(os.path.normpath('C:\repos\neuro_cognitiva\practica_1\atencionvisual'), info['participant'] + "_" + info['dateStr'])


#%% Genera la ventana
# win = visual.Window(size=[2880, 1800], color=[-1,-1,-1], screen = 0, fullscr = True, allowStencil = True)
win = visual.Window(size=[1400, 800], color=[-1,-1,-1], screen = 0, fullscr = True, allowStencil = True)

# win.setMouseVisible(False)
fontsize=0.15

#%% Genero texturas
# Generamos cruz de fijación 
#initialise some stimuli
#fixation = visual.Circle(win, size = 5, lineColor = 'white', fillColor = 'lightGrey')
inicio = visual.TextStim(win,text='Bienvenidxs',
                         font = 'Arial', color = 'white', 
                         anchorHoriz = 'center', pos=(0.0,.5)) 

instructions_header = visual.TextStim(win, text='INSTRUCCIONES', 
                                      font = 'Arial', color = 'white', 
                                      anchorHoriz = 'center', pos=(0.0,.5))


instrucciones = visual.TextStim(win,
                                text='Si el circulo verde aparece a la derecha tenes que tocar la flecha derecha. Si aparece de la izquierda, la flecha izquierda',
                                font = 'Arial', color = 'white', 
                                anchorHoriz = 'center', pos=(0.0,.5)) 

comienzo = visual.TextStim(win,
                           text='Toque una tecla para comenzar...',
                           font = 'Arial', color = 'white', 
                           anchorHoriz = 'center', pos=(0.0,.5)) 

fin = visual.TextStim(win,
                     text='Gracias por participar',
                     font = 'Arial', color = 'white', 
                     anchorHoriz = 'center', pos=(0.0,.5)) 

fixation = visual.ShapeStim(
				win=win, name='polygon', vertices='cross',
			    size=(0.05, 0.05),
			    ori=0, pos=(0, 0),
			    fillColor=[1,1,1], fillColorSpace='rgb',
				lineColor = [-1,-1,-1],
			    opacity=1, depth=0.0, interpolate=True)



#run one trial
#Generamos el estímulo
probe = visual.GratingStim(win, size = 0.3, # 'size' is 3xSD for gauss,
    pos = [0.5, 0], #we'll change this later
    tex = None, mask = 'gauss',
    color = 'green')

# Generamos la clave (Triangulo)
cue = visual.ShapeStim(win,
    vertices = [[-0.1,-0.1], [-0.1,0.1], [0.1,0]],
    lineColor = 'red', fillColor = 'salmon')

#%% Inicializo tiempos 

practice_clock = core.Clock()
experiment_clock = core.Clock()

#%% inicio

inicio.draw()
win.flip()
core.wait(2)

instrucciones.draw()
win.flip()
core.wait(3)
comienzo.draw()
win.flip()
event.waitKeys()

#Levanta las condiciones
conditions = data.importConditions('C:\\Users\\mluzb\\Documentos2\\docencia\\NC2024\\psycopy\\atencionVisual\\conditions.csv')
trials = data.TrialHandler(trialList=conditions, nReps=2)
#add trials to the experiment handler to store data
thisExp = data.ExperimentHandler(
        name='Posner', version='1.0', #not needed, just handy
        extraInfo = info, #the info we created earlier
        dataFileName = filename, # using our string with data/name_date
        )
thisExp.addLoop(trials) #there could be other loops (like practice loop)

respClock = core.Clock()
#clock reset
win.flip()
elapse_time = 0
last_trial_dur = 0
experiment_clock.reset()


elapse_time = 0
last_trial_dur = 0

for thisTrial in trials:
    #cambia la orientación de la clave según csv
    
    probe.setPos( [thisTrial['probeX'], 0] )
    cue.setOri( thisTrial['CueOri'] )
    fixation_dur =  int(random.gauss(thisTrial['fixtime'],0.1)*frs)
    probe_dur = int(info['probeTime']*frs) # Siempre en frames
    cue_dur = int(info['cueTime']*frs) # Siempre en frames
    elapse_time += last_trial_dur
    response_dur = random.gauss(2 ,0.5)*frs
    fixation_onset = elapse_time
    pre_blank_onset = fixation_onset + fixation_dur
    cue_onset = elapse_time + fixation_dur 
    probe_onset = elapse_time + fixation_dur + cue_dur
    response_onset = elapse_time + fixation_dur   
    
    for s in range(int(fixation_dur)):
        fixation.draw()
        win.flip()
    rt_cue = experiment_clock.getTime()
    for p in range(int(cue_dur)):
        cue.draw()
        win.flip()

    start_stimulus = experiment_clock.getTime()
    # rt_probe = experiment_clock.getTime()
    responded = False
    response = []
    resp    = []
    rt = 'NR'
    event.clearEvents(eventType=None)
    start_response = experiment_clock.getTime()
    rt_probe = start_stimulus
    for rr in range(int(response_dur)): # Grafica el estimulo
        
        if rr<int(probe_dur):
            probe.draw()
            win.flip()
        else:
            win.flip()
    #response collection
        if not responded:
            response = event.getKeys(keyList=['left','right'], timeStamped=True)
            if len(response) > 0:
                responded = True
                cumulative_response_time = round(experiment_clock.getTime(),3)
                rt = round(experiment_clock.getTime() - start_response,3)
                resp=response[0][0]
                
    print(rt)
    print(resp)        
    # Chequea la respuesta
    if thisTrial['probeX']>0 and resp=='right':
        corr = 1
    elif thisTrial['probeX']<0 and resp=='left':
        corr = 1
    else:
        corr = 0
    #Guarda la información
    trials.addData('resp', resp)
    trials.addData('rt', rt)
    trials.addData('rt_cue', rt_cue)
    trials.addData('rt_probe', rt_probe)
    trials.addData('corr', corr)
    thisExp.nextEntry()

fin.draw()
win.flip()
core.wait(5)
win.close()
core.quit()

