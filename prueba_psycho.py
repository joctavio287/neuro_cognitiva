from psychopy import visual, core

win = visual.Window(screen=0)
msg = visual.TextStim(win, text=u"\u00A1Hola mundo!")

msg.draw()
core.wait(5)

win.flip()
core.wait(5)
win.close()