from pygame import *
from interface import *
from pointer import *

screen = display.set_mode((800,600))
running = True

class Derp():
    def __init__(self):
        self.value = 20
        
class globalz():
    lolwut = Derp()
    
myinput = NumericInput(Pointer(Pointer(globalz,"lolwut"),"value"),100,200)
clock = time.Clock()

while running:
    for evt in event.get():
        if evt.type == QUIT:
            running = False
        elif evt.type == MOUSEBUTTONDOWN:
            if myinput.rect.collidepoint(*evt.pos):
                myinput.onClick(event,screen)
    myinput.render(screen)
    display.flip()
    clock.tick(60)
quit()
