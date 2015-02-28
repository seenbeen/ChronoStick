from pygame import *
from random import *
import math

font.init()
timesFont = font.SysFont("Times New Roman", 14)

class MainInterface:
    def __init__(self):
        self.windows = []
        # Inputs will be processed by the main loop
        #  of the interface and components will be
        #  passed to children
        
        self.inputs = {"mx":None,"my":None,
                       "mb":None,
                       "kb":None,
                       "events":None}
        self.Events = []
        
    def updateInputs(self,mx,my,mb,kb,events):
        self.inputs["mx"] = mx
        self.inputs["my"] = my
        self.inputs["mb"] = mb
        self.inputs["kb"] = kb
        self.inputs["events"] = events

    #  Called every round of update loop;
    #  Assumes: all input is fetched before this is called
    #  Passes in each input to each BasicWindow component
    
    def mainUpdate(self):
        for wind in self.windows:
            wind.updateInputs(self.inputs)
            wind.update()
        for evt in self.Events:
            self.processEvent(evt)
            
    def mainRender(self,screen):
        screen.fill((0,0,0))
        for wind in self.windows[::-1]:
            wind._render(screen)

    #Note: perform a "newfocus" check before applying the update
    #      to the first window (presumably the focus) in windows
    def processEvent(self,evt):
        # ShiP -> Shift window priority to the front
        if evt.type == "ShiP":
            for i in range(len(self.windows)):
                if self.windows[i].id == evt.properties["id"]:
                    wind = self.windows[i]
                    self.windows = self.windows[:i]+self.windows[i+1:]
                    self.windows = [wind]+self.windows

    def addWindow(self,wind):
        self.windows = [wind]+self.windows
        
class Component:
    IDs = 0
    def __init__(self,rect,colour = [0,255,0]):
        self.rect = Rect(*rect)
        self.colour = colour
        #register this Component
        self.id = Component.IDs
        Component.IDs+=1

    def shiftPos(self,dx,dy):   
        self.pos[0] += dx
        self.pos[1] += dy

    def localCoords(self,mx,my,direction = 1):
        return (mx-self.rect.x*direction,my-self.rect.y*direction)
    
    def render(self,screen,shift = [0,0]):
        draw.rect(screen,self.colour,self.rect.move(*shift)) #debug purposes
        draw.rect(screen,(0,0,0),self.rect.move(*shift),2) #debug purposes
        
class BasicWindow(Component):
    def __init__(self,rect):
        super().__init__(rect)
        #self.moveable = moveable #unsupported atm
        self.components = []
        self.init()
        self.inputs = {"mx":None,"my":None,
                       "mb":None,
                       "kb":None,
                       "events":None}
    
    def init(self):
        #this is the init that children will use to define
        # their own components
        return

    def update(self):
        #to be inplemented by children
        return
    
    def updateInputs(self,inputs):
        self.inputs = inputs
    
    def _render(self,screen):
        super().render(screen)
        screen.set_clip(self.rect)
        self.render(screen)
        for comp in self.components:
            comp.render(screen,self.rect.topleft)
        screen.set_clip(None)

    def render(self,screen):
        return #this is defined by any extending classes
    
class BasicButton(Component):
    def __init__(self,l,h):
        super().__init__([0,0,l,h])
        
    def collidePoint(self,x,y):
        return self.rect.collidepoint(x,y)

    def onHover(self):
        return #for buttons to implement

    def offHover(self):
        return #for buttons to implement
    
    def onClick(self):
        return #for buttons to implement
    
    def onUnClick(self):
        return #for buttons to implement

    def onClickHold(self):
        return #for buttons to implement
    
    #Note: Render can also be redefined - for now it just draws
    #      a box around its dimensions and location in the colour
    #      specified

class BasicRightClickMenu(BasicWindow):
    def __init__(self,rect,name):
        self.buttons = []
        self.name = name
        super().__init__(rect)
        self.colour = (235,235,235)
        self.oldRect = self.rect.copy()
        self.animFrame = 0
        self.frameNumber = 10
        self.hidden = True
        self.animState = "open"
        
    def addButton(self,button):
        butth = 5+len(self.buttons)*22
        button.rect = button.rect.move(5,butth)
        
        self.rect.height = max(butth+27,self.rect.height)
        
        self.rect.width = max(button.rect.width+10,self.rect.width)

        for butt in self.buttons:
            maxWidth = max(button.rect.width,butt.rect.width)
            butt.rect.width = maxWidth
            button.rect.width = maxWidth
            
        self.components.append(button)
        self.buttons.append(button)    

    def showMenu(self,x,y):
        self.setLocation(x,y)
        self.animFrame = 0
        self.hidden = False
        self.rect.width = 0
        self.rect.height = 0
        self.animState = "opening"
        
    def hideMenu(self):
        self.animState = "closing"
        self.animFrame-=1
        
    def setLocation(self,x,y):
        dx = x-self.rect.x
        dy = y-self.rect.y
        self.rect.move_ip(dx,dy)

    def update(self):
        if self.hidden:
            return
        if self.animState == "open":
            mx = self.inputs["mx"]
            my = self.inputs["my"]
        
            for butt in self.buttons:
                if butt.collidePoint(*self.localCoords(mx,my)):
                    butt.onHover()
                else:
                    butt.offHover()
            for evt in self.inputs["events"]:
                if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                    for butt in self.buttons:
                        if butt.collidePoint(*self.localCoords(evt.pos[0],
                                                               evt.pos[1])):
                            self.buttonClicked(butt.name)
        elif self.animFrame > self.frameNumber and self.animState == "opening":
            self.animState = "open"
        elif self.animFrame == -1 and self.animState == "closing":
            self.hidden = True
            self.animState = "closed"
            for butt in self.buttons:
                butt.offHover()
        else:
            scale = self.animFrame/self.frameNumber
            self.rect.width = int(self.oldRect.width*scale)
            self.rect.height = int(self.oldRect.height*scale)
            if self.animState == "opening":
                self.animFrame+=1
            if self.animState == "closing":
                self.animFrame-=1
            
    def _render(self,screen):
        if self.hidden:
            return
        super()._render(screen)
    def buttonClicked(self,button_name):
        return #to be implemented by a RightClickMenu
    
class RightMenuButton(BasicButton):
    def __init__(self,text,name):
        self.fontimg = timesFont.render(text,True,(0,0,0))
        super().__init__(self.fontimg.get_width()+10,20)
        self.colour = (200,200,200)
        self.name = name
        
    def onHover(self):
        self.colour = (100,100,100)

    def offHover(self):
        self.colour = (200,200,200)

    def render(self,screen,shift = [0,0]):
        super().render(screen,shift)
        screen.blit(self.fontimg,(self.rect.x+shift[0]+5,
                                  self.rect.y+shift[1]+3))

class Label(Component):
    def __init__(self,text,pos):
        self.fontimg = timesFont.render(text,True,(0,0,0))
        super().__init__([pos[0],pos[1],self.fontimg.get_width()+10,20])
        self.colour = (255,255,255)
        
    def render(self,screen,shift = [0,0]):
        #super().render(screen,shift)
        screen.blit(self.fontimg,(self.rect.x+shift[0]+5,
                                  self.rect.y+shift[1]+3))

class DynamicLabel(Label):
    def __init__(self,ptr,pos):
        self.ptr = ptr
        super().__init__(str(ptr.getVal()),pos)
        self.oldVal = str(ptr.getVal())
        
    def render(self,screen,shift = [0,0]):
        newVal = str(self.ptr.getVal())
        if self.oldVal != newVal:
            self.oldVal = newVal
            self.fontimg = timesFont.render(newVal,True,(0,0,0))
        super().render(screen,shift)
        
class KFrameButton(BasicButton):
    def __init__(self,rect,frame):
        super().__init__(rect[2],rect[3])
        self.rect.move_ip(rect[0],rect[1])
        self.colour = (255,255,255)
        self.frame = frame
        self.oldT = frame.time
        
    def onHover(self):
        self.colour = (100,100,255)

    def offHover(self):
        self.colour = (255,255,255)

    def updateRequired(self):
        return self.oldT != self.frame.time
    
class TextInput(Component):
        
    def __init__(self,rect,ptr,txtlen):
        super().__init__(rect)
        self.ptr = ptr
        self.active = True
        self.oValue = ""
        self.value = ""
        self.fontimg = self.refreshTextImg()
        self.txtlen = txtlen
        self.colour = (255,255,255)
        self.carriage = len(self.value)
        self.carriageTimer = 0
        self.carriagex = 0 #where carriage is atm
        
    # Stuff to be replaced if any restrictions are required on the input
    '''each character typed is passed to the function and is only
       added as a value if restrict returns True'''
    def restrict(self,char):
        return True
    '''only assign the value to the bounded pointer if validate
       returns true (ie: this is valid input)'''
    def validate(self,text):
        return True
    '''datatype provides the value typed and returns the value
       that will be assigned to the bounded pointer'''
    def datatype(self,text):
        return text
    '''called when onClick occurs and returns
       a string to be assigned as the starting
       value of the textfield'''
    def textConvert(self,value):
        return str(value)
    
    def refreshTextImg(self,n=None):
        if n != None:
            return timesFont.render(self.value[:n],True,(0,0,0))
        else:
            return timesFont.render(self.value,True,(0,0,0))

    def setVal(self):
        if self.validate(self.value):
            var = self.datatype(self.value)
            self.ptr.setVal(var)
            self.oValue = self.value
        else:
            self.value = self.oValue

    def onHover(self):
        self.colour = (100,100,255)
    def offHover(self):
        self.colour = (255,255,255)
        
    def onClick(self,event,screen,shift):
        self.colour = (100,255,100)
        screen.set_clip(self.rect.move(*shift))
        self.carriage = len(self.value)
        self.carriageTimer = 0
        self._onClick(event,screen,shift)
        self.value = self.oValue
        self.fontimg = self.refreshTextImg()
        self.colour = (255,255,255)
        screen.set_clip(None)
    
    def _onClick(self,event,screen,shift):
        while True:
            for evt in event.get():
                if evt.type == QUIT:
                    return
                elif evt.type == KEYDOWN:
                    if evt.key == K_ESCAPE:
                        self.value = self.oValue
                        return
                    elif evt.key == K_KP_ENTER or evt.key == K_RETURN:
                        self.setVal()
                        return
                    elif evt.key == K_BACKSPACE:    # remove letter at carriage
                        if self.carriage>0:
                            self.value = self.value[:self.carriage-1]+self.value[self.carriage:]
                            self.carriage -= 1
                        self.fontimg = self.refreshTextImg()
                    elif evt.key == K_LEFT:
                        if self.carriage > 0:
                            self.carriage -= 1
                    elif evt.key == K_RIGHT:
                        if self.carriage < len(self.value):
                            self.carriage += 1
                    elif evt.key < 256:
                        if self.restrict(evt.unicode):
                            if len(self.value) < self.txtlen:
                                if self.carriage == len(self.value):
                                    self.value += evt.unicode
                                else:
                                    self.value = self.value[:self.carriage]+evt.unicode+self.value[self.carriage:]
                                self.carriage+=1
                            else:
                                if self.carriage == len(self.value):
                                    self.value = self.value[:-1]+evt.unicode
                                    
                            self.fontimg = self.refreshTextImg()
                elif evt.type == MOUSEBUTTONDOWN:
                    if evt.button == 1:
                        if not self.rect.collidepoint(*evt.pos):
                            self.setVal()
                            return

            self.render(screen,shift)
            
            #show the carriage
            self.carriagex = self.refreshTextImg(self.carriage).get_width()
            if self.carriageTimer < 800:
                draw.line(screen,(0,0,0),
                          (self.rect.x+3+self.carriagex+shift[0],self.rect.y+3+shift[1]),
                          (self.rect.x+3+self.carriagex+shift[0],self.rect.y+self.rect.h-3+shift[1]),1)
            elif self.carriageTimer == 1600:
                self.carriageTimer = 0
            self.carriageTimer += 1
            display.flip()

    def manualUpdate(self):
        self.oValue = self.textConvert(self.ptr.getVal())
        if len(self.oValue) > self.txtlen:
            self.oValue = self.oValue[:self.txtlen]
        self.value = self.oValue
        self.fontimg = self.refreshTextImg()

    def softReset(self):
        self.value = ""
        self.fontimg = self.refreshTextImg()
        
    def render(self,screen,shift = [0,0]):
        super().render(screen,shift)
        offset = 0
        if self.carriagex > self.rect.w-5:
            offset = self.rect.w-5-self.carriagex
        screen.blit(self.fontimg,(self.rect.x+3+shift[0]+offset,self.rect.y+2+shift[1]))
        
class NumericInput(TextInput):
    def __init__(self,pointer,x,y):
        super().__init__([x,y,100,20],pointer,10)

    def validate(self,text):
        try:        
            i = float(text)
            return True
        except ValueError:
            return False
        
    def datatype(self,text):
        return float(text)

    def restrict(self,char):
        if char.isdigit():
            return True
        if (char == "-" and self.carriage == 0 and self.value.count("-") == 0):
            return True
        if (char == "." and self.value.count(".") == 0):
            return True
        return False

class IntegerInput(TextInput):
    def __init__(self,pointer,x,y):
        super().__init__([x,y,100,20],pointer,10)
        
    def validate(self,text):
        try:
            i = int(text)
            return True
        except ValueError:
            return False

    def datatype(self,text):
        return int(text)

    def restrict(self,char):
        if char.isdigit():
            return True
        if (char == "-" and self.carriage == 0 and self.value.count("-") == 0):
            return True
        return False

class AngularInput(NumericInput):
    def textConvert(self,value):
        return str(math.degrees(value))

    def datatype(self,text):
        return math.radians(float(text))

class CheckBoxButton(BasicButton):
    def __init__(self,w,h,pointer,mainVal,altVal):
        super().__init__(w,h)
        self.ptr = pointer
        self.state = 0
        self.valueStates = [altVal,mainVal]
        self.colour = (255,255,255)
        
    def manualUpdate(self):
        if self.ptr.getVal() == self.valueStates[0]:
            self.state = 0
        elif self.ptr.getVal() == self.valueStates[1]:
            self.state = 1
        else:
            self.state = 0
            self.ptr.setVal(self.valueStates[0])

    def onHover(self):
        self.colour = (100,100,255)

    def offHover(self):
        self.colour = (255,255,255)

    def onClick(self):
        self.state = (self.state+1)%2
        self.ptr.setVal(self.valueStates[self.state])

    def softReset(self):
        self.state = 0
        
    def render(self,screen,offset=[0,0]):
        super().render(screen,offset)
        if self.state == 1:
            tmp = self.rect.move(*offset)
            draw.line(screen,(0,0,0),tmp.topleft,tmp.bottomright,3)
            draw.line(screen,(0,0,0),tmp.topright,tmp.bottomleft,3)
