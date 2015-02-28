from pygame import *
from interface import *
from node import *
from pointer import *
import polyselect
import tools
from undoredo import *

screen = display.set_mode((1000,650))
display.set_caption("ChronoStick Editor v0.7 Alpha!")
running = True

class Globals:
    editorState = "standBy"
    curTool = "selectorTool"
    t = 0
    tLim = 60
    root = Node(325,250)
    tempFocus = None
    focus = None

    omx,omy = 0,0 #used by editor tools to track relative movement
    oang = 0 #see comment above ^
    orad = 0 #... see comment above xD

    rightClickMenu = "None"
    nodercmenu = None #placeholder
    keyrcmenu = None #moar placeholder
    lastrcmenu = None

    selectedFrame = None #used by the frame-data editor

    lassoed = [] #used by lassoed for insert keyframe and stuff
    highlightedFrame = None #used for deleteKeyFrame
    
    extruding = False #used by extrude node to assign new KeyFrame
                      #for first xform
    updateKeyFrameEditor = False #force an update into the keyframe editor

    errorMsg = ""
    helpMsg = ""

    onion = [] #onion :DD
    
    
class EditorWindow(BasicWindow):
    def init(self):
        xform0 = Globals.root.transforms[0]
        xform0.relativeRotation = False
        xform0.curveType = "Direct"

        node7 = Node(325,276)
        Globals.root.addChild(node7)
        node7.transforms[0].relativeRotation = False
        node7.transforms[0].angle = math.pi/2
        node8 = Node(325,216)
        Globals.root.addChild(node8)
        node8.transforms[0].relativeRotation = False
        node8.transforms[0].angle = -math.pi/2
        node9 = Node(305,310)
        node7.addChild(node9)
        node10 = Node(345,310)
        node7.addChild(node10)
        node11 = Node(306,222)
        node8.addChild(node11)
        node12 = Node(343,222)
        node8.addChild(node12)
        node13 = Node(295,245)
        node11.addChild(node13)
        node14 = Node(352,246)
        node12.addChild(node14)
        node15 = Node(301,345)
        node9.addChild(node15)
        node16 = Node(348,345)
        node10.addChild(node16)
        node17 = Node(325,196)
        node8.addChild(node17)
        node18 = Node(295,270)
        node13.addChild(node18)
        node19 = Node(352,271)
        node14.addChild(node19)
        
        
        Globals.root.setTime(Globals.t)
        Globals.root.refresh()
        Globals.root.getOnion(Globals.onion)

        #add some Dynamic Labels for help and error messages
        self.components.append(DynamicLabel(Pointer(Globals,"helpMsg"),
                                         (0,self.rect.h-50)))
        self.components.append(DynamicLabel(Pointer(Globals,"errorMsg"),
                                         (0,self.rect.h-20)))
        
    def selectPolygon(self,screen,event,preSelNode):
        tempRun = True
        screen.set_clip(self.rect)

        workingPts = []
        if preSelNode:
            workingPts.append(preSelNode)
            
        potentialPts = []
        Globals.root.grabChildren(potentialPts)
        lassoPts = []
        
        brect = [self.rect.w,self.rect.h,0,0]
        bgCopy = screen.subsurface(self.rect).copy()

        tempSurf = Surface((self.rect.w,self.rect.h),SRCALPHA)

        while tempRun:
            for evt in event.get():
                if evt.type == QUIT:
                    return []
                elif evt.type == MOUSEBUTTONUP:
                    if evt.button == 3:
                        tempRun = False
                        
            screen.blit(bgCopy,self.rect.topleft)
            mpos = mouse.get_pos()
            mpos = [mpos[0]-self.rect.x,
                    mpos[1]-self.rect.y]
            
            if mpos[0] < 0:
                mpos[0] = 0
            if mpos[0] > self.rect.w:
                mpos[0] = self.rect.w
            if mpos[1] < 0:
                mpos[1] = 0
            if mpos[1] > self.rect.h:
                mpos[1] = self.rect.h
                
            lassoPts.append(mpos)
            if mpos[0] > brect[2]:
                brect[2] = mpos[0]
            if mpos[0] < brect[0]:
                brect[0] = mpos[0]
            if mpos[1] > brect[3]:
                brect[3] = mpos[1]
            if mpos[1] < brect[1]:
                brect[1] = mpos[1]

            if len(lassoPts) > 1:
                tempSurf.fill((255,255,255,0))
                draw.polygon(tempSurf,(0,0,0),lassoPts,1)
                screen.blit(tempSurf,self.rect.topleft)

            #draw.rect(screen,(0,255,0),(self.rect.x+brect[0],
            #                            self.rect.y+brect[1],
            #                            brect[2]-brect[0],
            #                            brect[3]-brect[1]),2)

            display.flip()
            myClock.tick(60)
        screen.set_clip(None)
        rkt = Rect(brect[0],brect[1],
                   brect[2]-brect[0],
                   brect[3]-brect[1])
        
        for n in potentialPts:
            if preSelNode and preSelNode.id == n.id:
                continue
            if polyselect.withinPoly(n.displayCoords(),lassoPts,rkt):
                workingPts.append(n)

        return workingPts

    def update(self):
        if Globals.focus == None:
            Globals.helpMsg = "Select a Node to Edit it."
            
        mx,my = self.inputs["mx"],self.inputs["my"]
        mx,my = self.localCoords(mx,my)
        
        for evt in self.inputs["events"]:
            if Globals.editorState == "standBy":
                if evt.type == KEYDOWN:
                    if Globals.focus != None:
                        toolFlag = False
                        if evt.key == K_q:
                            Globals.curTool = "selectorTool"
                            toolFlag = True
                        if evt.key == K_w:
                            Globals.curTool = "scaleTool"
                            toolFlag = True
                        if evt.key == K_e:
                            Globals.curTool = "extrudeTool"
                            toolFlag = True
                        if evt.key == K_r:
                            Globals.curTool = "rotateTool"
                            toolFlag = True
                        if evt.key == K_f:
                            Globals.curTool = "scaleChildTool"
                            toolFlag = True
                        if evt.key == K_g:
                            Globals.curTool = "rotateChildTool"
                            toolFlag = True
                        if toolFlag:
                            Globals.tempFocus = None
                    if self.inputs["kb"][K_LCTRL]:
                        if evt.key == K_z:
                            UndoRedo.undo()
                            Globals.root.refresh()
                        elif evt.key == K_y:
                            UndoRedo.redo()
                            Globals.root.refresh()
                            
                if Globals.curTool == "selectorTool":
                    Globals.tempFocus = Globals.root.collideMouse(mx,my,7)
                else:
                    tempNode = Globals.root.collideMouse(mx,my)
                    if tempNode != None and tempNode.id == Globals.focus.id:
                        Globals.tempFocus = Globals.focus
                    else:
                        Globals.tempFocus = None
                        
                if evt.type == MOUSEBUTTONDOWN:
                    if evt.button == 1 and self.rect.collidepoint(*evt.pos):
                        Globals.selectedFrame = None
                        if Globals.curTool == "selectorTool":
                            Globals.focus = Globals.tempFocus
                        elif Globals.curTool != "selectorTool":
                            posx,posy = self.localCoords(evt.pos[0],evt.pos[1])
                            collisionTest = Globals.focus.collideMouse(posx,posy,7)
                            #Note: None == False in terms of boolean logic
                            if collisionTest and collisionTest.id == Globals.focus.id:
                                Globals.tempFocus = None
                                tmp = self.localCoords(Globals.focus.x,
                                                       Globals.focus.y,-1)
                                Globals.omx,Globals.omy = tmp
                                Globals.oang = Globals.focus.angle
                                Globals.orad = Globals.focus.radius
                                Globals.editorState = "toolDrag"
                                
            elif Globals.editorState == "rightClick":
                if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                    Globals.editorState = "standBy"
                    Globals.lastrcmenu.hideMenu()
                    Globals.lassoed = []
                    Globals.highlightedFrame = None
                    
            #Right-Click Menus
            if evt.type == MOUSEBUTTONDOWN and evt.button == 3:
                if Globals.editorState == "standBy" and Globals.nodercmenu.hidden:
                    if self.rect.collidepoint(*evt.pos):
                        posx,posy = self.localCoords(evt.pos[0],evt.pos[1])
                        collisionTest = Globals.root.collideMouse(posx,posy,7)
                        Globals.lassoed = self.selectPolygon(screen,event,collisionTest)

                        if len(Globals.lassoed) > 0:
                            newPt = tools.avgPt(Globals.lassoed)
                            Globals.nodercmenu.showMenu(*self.localCoords(newPt[0],newPt[1],-1))
                            Globals.editorState = "rightClick"
                            Globals.lastrcmenu = Globals.nodercmenu

            #Return to standby if any dragging is occurring
            if evt.type == MOUSEBUTTONUP and evt.button == 1:
                if Globals.editorState == "toolDrag":
                    Globals.editorState = "standBy"
                    if Globals.extruding:
                        Globals.extruding = False
                        frame0 = Globals.focus.transforms[0]
                        frame0.angle = Globals.focus.angle
                        frame0.radius = Globals.focus.radius
                        UndoRedo.push([ExtrudeStep(Globals.focus,
                                                  Globals.focus.root)])
                    else:
                        undoredoSteps = [NodePropertyStep(Globals.focus,
                                                          "angle",
                                                          Globals.oang,
                                                          Globals.focus.angle),
                                         NodePropertyStep(Globals.focus,
                                                          "radius",
                                                          Globals.orad,
                                                          Globals.focus.radius)]
                        UndoRedo.push(undoredoSteps)
                        
        #viewing the current animation                            
        if Globals.editorState == "playAnim":
            Globals.t = (Globals.t+1)%(Globals.tLim+1)
            Globals.root.setTime(Globals.t)
            if Globals.focus != None:
                Globals.selectedFrame = Globals.focus.getKeyFrameAtTime(Globals.t)

        #if dragging is occurring, perform appropriate xforms
        elif Globals.editorState == "toolDrag":
            mx,my = self.localCoords(self.inputs["mx"],self.inputs["my"])
            tempAng = Globals.focus.fetchLocalAngle()
            root = Globals.focus.getRoot()
            ox,oy = self.localCoords(Globals.omx,Globals.omy)

            if Globals.curTool == "rotateTool":
                mouseAng = 0
                if self.inputs["kb"][K_LSHIFT] or self.inputs["kb"][K_LALT]:
                    oldVect = [ox-root.x,oy-root.y]
                    tempVect = [ox-root.x,oy-root.y]
                    if self.inputs["kb"][K_LSHIFT]:
                        tempVect[0] += mx-ox
                    if self.inputs["kb"][K_LALT]:
                        tempVect[1] += my-oy
                    Globals.focus.radius = math.hypot(*tempVect)
                    mouseAng = cstickmath.vectAngle(oldVect,tempVect)
                else:
                    Globals.focus.radius = Globals.orad
                    mouseAng = cstickmath.vectAngle([ox-root.x,oy-root.y],
                                            [mx-root.x,my-root.y])
                if mouseAng > math.pi:
                    mouseAng -= 2*math.pi
                Globals.focus.angle = Globals.oang+mouseAng
            elif Globals.curTool == "extrudeTool":
                newNode = Node(Globals.focus.x+50,Globals.focus.y)
                Globals.focus.addChild(newNode)
                Globals.focus = newNode
                Globals.curTool = "rotateTool"
                Globals.oang = Globals.focus.angle
                Globals.orad = Globals.focus.radius
                Globals.omx,Globals.omy = self.localCoords(newNode.x,
                                                           newNode.y,-1)
                Globals.extruding = True                
            elif Globals.curTool == "scaleTool":
                v1 = [Globals.focus.x-root.x,Globals.focus.y-root.y]
                v2 = [mx-root.x,my-root.y]
                r = tools.projMag(v2,v1)
                Globals.focus.radius = abs(r)
            #elif Globals.curTool == "rotateChildTool":
                
            Globals.root.refresh()

    def renderOnion(self,screen):
        ox,oy = self.rect.topleft
        for x in Globals.onion:
            for c in x[1]:
                draw.line(screen,(122,122,122),
                          (ox+x[0][0],oy+x[0][1]),
                          (ox+c[0],oy+c[1]),2)
        
    def render(self,screen):
        screen.fill((255,255,255))
        renderQueue = []
        Globals.root.grabChildren(renderQueue)
        nodeDict = {}
        for x in renderQueue:
            nodeDict[x.id] = x
            tmp = self.localCoords(x.x,x.y,-1)
            x.extraData["renderCoords"] = [int(tmp[0]),int(tmp[1])]
        renderQueue.sort(key=lambda x: x.zProp)
        for x in renderQueue:
            if x.validScript:
                try:
                    x.render(x,screen,nodeDict)
                except Exception as err:
                    Globals.errorMsg = "Render Function Error: "+str(err)
        if Globals.editorState != "playAnim":
            self.renderOnion(screen)
            Globals.root._render(screen,(self.rect.x,self.rect.y))
            if Globals.focus != None:
                focusPos = Globals.focus.displayCoords()
                focusPos = self.localCoords(focusPos[0],focusPos[1],-1)
                draw.circle(screen,(0,255,0),focusPos,7)
                draw.circle(screen,(0,0,0),focusPos,7,1)
                
            if Globals.tempFocus != None:
                focusPos = Globals.tempFocus.displayCoords()
                focusPos = self.localCoords(focusPos[0],focusPos[1],-1)
                draw.circle(screen,(30,200,255),focusPos,7)
                draw.circle(screen,(0,0,0),focusPos,7,1)

            if len(Globals.lassoed) > 0:
                for n in Globals.lassoed:
                    nPos = n.displayCoords()
                    nPos = self.localCoords(nPos[0],nPos[1],-1)
                    draw.circle(screen,(30,100,255),nPos,7)
                    draw.circle(screen,(0,0,0),nPos,7,1)
        else:
            Globals.root._render(screen,(self.rect.x,self.rect.y),False)
            
        
                
class KeyFrameWindow(BasicWindow):
    def init(self):
        # at this point, rectangle dimensions have already been set
        # so this is a perfectly safe assignment of value
        h = int(self.rect.y+self.rect.height*0.5)
        self.startPos = (self.rect.x+int(self.rect.width*0.1),h)
        self.endPos = (self.rect.x+int(self.rect.width*0.90),h)
        self.indicatorPoly = ((0,0),(5,-5),(5,-18),(-5,-18),(-5,-5))

        #set up an indicator rect pos for drag-n-drop-timeline
        posx = self.startPos[0]+(self.endPos[0]-self.startPos[0])*Globals.t/Globals.tLim
        posy = self.rect.y+int(self.rect.height*0.4)
        poly = list(map(lambda x:(x[0]+posx,x[1]+posy),
                                          self.indicatorPoly))
        self.indicatorRect = Rect(poly[-2][0],poly[-2][1],10,15)
        
        self.playPauseButton = {"state":0,"states":["standBy","playAnim"],
                                "rect":Rect(self.rect.x+int(self.rect.width*0.01),
                                        self.rect.y+int(self.rect.height*0.35),
                                        int(self.rect.width*0.07),
                                        int(self.rect.height*0.30))}
        self.dragOffset = [0,0]
        self.oldFocus = None

        self.buttons = []

        self.components.append(Label("Time Line:",(0,0)))
        self.components.append(Label("T: ",(590,5)))
        self.components.append(DynamicLabel(Pointer(Globals,"t"),(610,5)))
        
    def playPause(self):
        self.playPauseButton["state"] = (self.playPauseButton["state"]+1)%2
        s = self.playPauseButton["state"] #preventing unnecessarily long lines.
        Globals.editorState = self.playPauseButton["states"][s]
        Globals.tempFocus = None
        
    def update(self):
        #buttons for selecting keyframes
        if Globals.editorState == "standBy":
            for butt in self.buttons:
                if butt.collidePoint(self.inputs["mx"],self.inputs["my"]):
                    butt.onHover()
                else:
                    butt.offHover()
        
        for evt in self.inputs["events"]:
            if evt.type == KEYDOWN:
                if evt.key == K_SPACE:
                    if Globals.editorState == "standBy" or Globals.editorState == "playAnim":
                        self.playPause()
                        
            if evt.type == MOUSEBUTTONDOWN:
                if evt.button == 1:
                    #checking for play/pause
                    if self.playPauseButton["rect"].collidepoint(evt.pos):
                        self.playPause()

                    elif Globals.editorState == "standBy":
                        #dragging the time bar
                        if self.indicatorRect.collidepoint(evt.pos):
                            Globals.editorState = "timeDrag"
                            self.dragOffset = [evt.pos[0]-self.indicatorRect[0],
                                               evt.pos[1]-self.indicatorRect[1]]
                        else:
                            pressed = False
                            for butt in self.buttons:
                                if butt.collidePoint(*evt.pos):
                                    Globals.selectedFrame = butt.frame
                                    pressed = True
                                    break
                            if not pressed and self.rect.collidepoint(*evt.pos):
                                Globals.selectedFrame = None
                elif evt.button == 2:
                    if Globals.editorState == "standBy":
                        if self.indicatorRect.collidepoint(evt.pos):
                            Globals.editorState = "timeDrag set"
                            self.dragOffset = [evt.pos[0]-self.indicatorRect[0],
                                               evt.pos[1]-self.indicatorRect[1]]
                    for butt in self.buttons:
                        if butt.collidePoint(*evt.pos):
                            Globals.selectedFrame = butt.frame
                            Globals.t = butt.frame.time
                            Globals.root.setTime(Globals.t)
                            Globals.root.refresh()
                            Globals.onion = []
                            Globals.root.getOnion(Globals.onion)
                            break
                elif evt.button == 3 and Globals.editorState == "standBy":
                    for butt in self.buttons:
                        if butt.collidePoint(*evt.pos):
                            Globals.keyrcmenu.showMenu(evt.pos[0],
                                                       evt.pos[1]-100)
                            Globals.editorState = "rightClick"
                            Globals.lastrcmenu = Globals.keyrcmenu
                            Globals.highlightedFrame = butt.frame
                            
            elif evt.type == MOUSEBUTTONUP:
                if evt.button == 1 and Globals.editorState == "timeDrag":
                    Globals.editorState = "standBy"
                elif evt.button == 2 and Globals.editorState == "timeDrag set":
                    Globals.editorState = "standBy"
                    
        if Globals.editorState == "timeDrag" or Globals.editorState == "timeDrag set":
            if self.inputs["mx"]+self.dragOffset[0] == self.startPos[0]:
                Globals.t = 0
            else:
                Globals.t = (self.inputs["mx"]+self.dragOffset[0]-self.startPos[0])/(self.endPos[0]-self.startPos[0])*Globals.tLim
                Globals.t = int(max(0,min(Globals.tLim,Globals.t)))
            if Globals.editorState == "timeDrag set":
                Globals.root.setTime(Globals.t)
            if Globals.focus != None:
                Globals.selectedFrame = Globals.focus.getKeyFrameAtTime(Globals.t)
                
        self.updateButtons()

    def updateButtons(self):
        #when a new keyframe is added (or undo redo or whatever), updates buttons
        if self.oldFocus != None and (len(self.buttons) != len(self.oldFocus.transforms)
                                      or Globals.updateKeyFrameEditor):
            Globals.updateKeyFrameEditor = False
            self.oldFocus = None
            
        if self.oldFocus == None and Globals.focus == None:
            return
        elif self.oldFocus != None and Globals.focus == None:
            self.buttons = []
            self.oldFocus = None
            return
        elif self.oldFocus != None and Globals.focus != None and self.oldFocus.id  == Globals.focus.id:
            for butt in self.buttons:
                if butt.updateRequired():
                    t = butt.frame.time
                    posx = self.startPos[0]+(self.endPos[0]-self.startPos[0])*t/Globals.tLim
                    posy = self.rect.y+int(self.rect.height*0.35)
                    butt.rect.topleft = (posx-3,posy)
                    butt.oldT = t
            return
        else:
            self.oldFocus = Globals.focus
            self.buttons = []
            for x in Globals.focus.transforms:
                t = x.time
                posx = self.startPos[0]+(self.endPos[0]-self.startPos[0])*t/Globals.tLim
                posy = self.rect.y+int(self.rect.height*0.4)
                newButt = KFrameButton([posx-3,posy,
                                         6,int(self.rect.height*0.25)],x)
                self.buttons.append(newButt)
            
    def render(self,screen):
        screen.fill((155,155,155))
        
        #render the Time-Bar
        draw.line(screen,(0,190,255),self.startPos,self.endPos,2)
        #render the indicatorPoly
        posx = self.startPos[0]+(self.endPos[0]-self.startPos[0])*Globals.t/Globals.tLim
        posy = self.rect.y+int(self.rect.height*0.4)

        poly = list(map(lambda x:(x[0]+posx,x[1]+posy),
                                          self.indicatorPoly))
        self.indicatorRect = Rect(poly[-2][0],poly[-2][1],10,15)

        for butt in self.buttons:
            oldC = butt.colour
            if Globals.selectedFrame and butt.frame.id == Globals.selectedFrame.id:
                butt.colour = (0,255,0)
            butt.render(screen)
            butt.colour = oldC
        draw.polygon(screen,(255,0,0),poly)
        
        draw.line(screen,(200,0,0),(posx,posy),(posx,posy+int(self.rect.height*0.25)))

 #       for x in Globals.focus.transforms:
 #           kfx = self.startPos[0]+(self.endPos[0]-self.startPos[0])*Globals.t/Globals.tLim
 #           kfy = self.rect.y+int(self.rect.height*0.35)
            
        #Play/Pause Button
        draw.rect(screen,[(0,255,0),(0,155,0)][self.playPauseButton["state"]],
                                               self.playPauseButton["rect"])
        
class ToolButton(BasicButton):
    def __init__(self,name,description):
        super().__init__(40,40)
        self.colour = (0,255,0)
        self.oColour = (0,255,0)
        self.hoverColour = (160,0,0)
        self.onColour = (255,0,0)
        self.greyedOutColour = (0,100,0)
        self.holdColour = (255,100,100)
        self.name = name
        self.description = description
    def onHover(self):
        if Globals.curTool == self.name:
            self.colour = self.onColour
        else:
            self.colour = self.hoverColour
            if Globals.focus == None:
                self.colour = self.greyedOutColour
                
    def onClickHold(self):
        if Globals.curTool == self.name:
            self.colour = self.onColour
        else:
            self.colour = (255,100,100)
            if Globals.focus == None:
                self.colour = self.greyedOutColour
                
    def offHover(self):
        if Globals.curTool == self.name:
            self.colour = self.onColour
        else:
            self.colour = self.oColour
            if Globals.focus == None:
                self.colour = self.greyedOutColour
                
    def onUnClick(self):
        if Globals.focus != None:
            Globals.curTool = self.name
        
class SelectorButton(ToolButton):
    def __init__(self):
        super().__init__("selectorTool",
                         "Selector Tool (Q): Use this to select a Node to Edit.")

#single target node tools:
class TranslateButton(ToolButton):
    def __init__(self):
        super().__init__("extrudeTool",
                         "Extrude tool (E): Extrudes a Node from the Selected Node and rotates it.")
class ScaleButton(ToolButton):
    def __init__(self):
        super().__init__("scaleTool",
                         "Scale Tool (W): Scales the Selected Node's radius.")
class RotateButton(ToolButton):
    def __init__(self):
        super().__init__("rotateTool",
                         "Rotate Tool (R): Rotates/Translates the selected Node. Hold Alt/Shift to Lock Local Axes.")
#children target tools:
class ScaleChildrenButton(ToolButton):
    def __init__(self):
        super().__init__("scaleChildTool",
                         "Scale Children (S): Scales the Selected Node's Children's radii by percent. Hold alt to lock by 25%.")
        
class RotateChildrenButton(ToolButton):
    def __init__(self):
        super().__init__("rotateChildTool",
                         "Rotate Children (F): Rotates the node's children.")


class ToolbarWindow(BasicWindow):
    def init(self):
        self.buttons = []
        self.components.append(Label("Toolbar",(20,10)))
        self.addButton(SelectorButton(),20,40)
        self.addButton(ScaleButton(),20,100)
        self.addButton(TranslateButton(),20,160)
        self.addButton(RotateButton(),20,220)
        self.addButton(ScaleChildrenButton(),20,280)
        self.addButton(RotateChildrenButton(),20,340)
        
    def addButton(self,button,x,y):
        button.rect = button.rect.move(x,y)
        self.components.append(button)
        self.buttons.append(button)
        
    def update(self):
        mx = self.inputs["mx"]
        my = self.inputs["my"]
        Globals.helpMsg = "Hover over a Tool to learn about it."
        for butt in self.buttons:
            if butt.collidePoint(*self.localCoords(mx,my)):
                butt.onHover()
                Globals.helpMsg = butt.description
                
                if self.inputs["mb"][0] == 1:
                    butt.onClickHold()
            else:
                butt.offHover()
                
        for evt in self.inputs["events"]:
            if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                px,py = self.localCoords(*evt.pos)
                for butt in self.buttons:
                    if butt.collidePoint(px,py):
                        butt.onClick()
                        
            elif evt.type == MOUSEBUTTONUP and evt.button == 1:
                px,py = self.localCoords(*evt.pos)
                for butt in self.buttons:
                    if butt.collidePoint(px,py):
                        butt.onUnClick()
    
    def render(self,screen):
        screen.fill((220,220,220))

class PropertiesEditor(BasicWindow):
    def init(self):
        self.buttons = []
        self.nodeComponents = []
        self.kframeComponents = []
        self.components.append(Label("Node Editor: ID = ",(10,10)))
        self.components.append(DynamicLabel(Pointer(Pointer(Globals,"focus"),
                                                    "id"),(120,10)))
            
        self.components.append(Label("Radius:",(10,40)))
        radInput = NumericInput(Pointer(Pointer(Globals,"focus"),"radius"),60,41)
        self.components.append(radInput)
        self.nodeComponents.append(radInput)
        
        self.components.append(Label("Angle:",(10,70)))
        angInput = AngularInput(Pointer(Pointer(Globals,"focus"),
                                        "angle"),60,71)
        self.components.append(angInput)
        self.nodeComponents.append(angInput)

        self.components.append(Label("Rel Rotation:",(10,100)))
        relRotCheckBox = CheckBoxButton(20,20,Pointer(Pointer(Globals,"focus"),
                                                      "relRot"),
                                        True,False)
        relRotCheckBox.rect.move_ip(120,101)
        self.components.append(relRotCheckBox)
        self.nodeComponents.append(relRotCheckBox)
        
        self.components.append(Label("Direct Motion:",(10,130)))
        motionCheckBox = CheckBoxButton(20,20,Pointer(Pointer(Globals,"focus"),
                                                      "directMot"),
                                        True,False)
        motionCheckBox.rect.move_ip(120,131)
        self.components.append(motionCheckBox)
        self.nodeComponents.append(motionCheckBox)

        self.components.append(Label("Render Script:",(10,160)))
        renderScriptInput = RenderScriptInput(Pointer(Pointer(Globals,"focus"),
                                                      "renderScript"),
                                              10,190)
        self.components.append(renderScriptInput)
        self.nodeComponents.append(renderScriptInput)

        self.components.append(Label("KeyFrame Editor:",(10,250)))

        self.components.append(Label("Time:",(10,280)))
        timeInput = TimeInput(Pointer(Pointer(Globals,"selectedFrame"),
                                      "time"),60,281)
        self.components.append(timeInput)
        self.kframeComponents.append(timeInput)
        
        self.components.append(Label("Radius:",(10,310)))
        radInput = NumericInput(Pointer(Pointer(Globals,"selectedFrame"),
                                        "radius"),60,311)
        self.components.append(radInput)
        self.kframeComponents.append(radInput)
        
        self.components.append(Label("Angle:",(10,340)))
        angInput = AngularInput(Pointer(Pointer(Globals,"selectedFrame"),
                                        "angle"),60,341)
        self.components.append(angInput)
        self.kframeComponents.append(angInput)

        self.components.append(Label("Rel Rotation:",(10,370)))
        relRotCheckBox = CheckBoxButton(20,20,Pointer(Pointer(Globals,"selectedFrame"),
                                                      "relativeRotation"),
                                        True,False)
        relRotCheckBox.rect.move_ip(120,371)
        self.components.append(relRotCheckBox)
        self.kframeComponents.append(relRotCheckBox)
        
        self.components.append(Label("Direct Motion:",(10,400)))
        motionCheckBox = CheckBoxButton(20,20,Pointer(Pointer(Globals,"selectedFrame"),
                                                      "curveType"),
                                        "Direct","Smooth")
        motionCheckBox.rect.move_ip(120,401)
        self.components.append(motionCheckBox)
        self.kframeComponents.append(motionCheckBox)
            
    def updateComponentSet(self,SET):
        mx,my = self.inputs["mx"],self.inputs["my"]
        for butt in SET:
            if Globals.editorState == "standBy":
                if butt.rect.collidepoint(*self.localCoords(mx,my)):
                    butt.onHover()
                else:
                    butt.offHover()
            butt.manualUpdate()
        if Globals.editorState == "standBy":
            for evt in self.inputs["events"]:
                if evt.type == MOUSEBUTTONDOWN:
                    if evt.button == 1:
                        for butt in SET:
                            if butt.rect.collidepoint(*self.localCoords(evt.pos[0],
                                                                        evt.pos[1])):
                                oldFrameData = []
                                if SET is self.nodeComponents:
                                    oldFrameData = [Globals.focus.angle,
                                                    Globals.focus.radius,
                                                    Globals.focus.relRot,
                                                    Globals.focus.directMot]
                                elif SET is self.kframeComponents:
                                    oldFrameData = [Globals.selectedFrame.angle,
                                                    Globals.selectedFrame.radius,
                                                    Globals.selectedFrame.relativeRotation,
                                                    Globals.selectedFrame.curveType,
                                                    Globals.selectedFrame.time]
                                    
                                if isinstance(butt,BasicButton):
                                    butt.onClick()
                                else:
                                    butt.onClick(event,screen,self.rect.topleft)

                                newFrameData = []
                                
                                if SET is self.nodeComponents:
                                    newFrameData = [Globals.focus.angle,
                                                    Globals.focus.radius,
                                                    Globals.focus.relRot,
                                                    Globals.focus.directMot]    
                                elif SET is self.kframeComponents:
                                    newFrameData = [Globals.selectedFrame.angle,
                                                    Globals.selectedFrame.radius,
                                                    Globals.selectedFrame.relativeRotation,
                                                    Globals.selectedFrame.curveType,
                                                    Globals.selectedFrame.time]
                                    
                                if tools.difference(oldFrameData,newFrameData):
                                    undoredolst = []

                                    if SET is self.nodeComponents:
                                        undoredolst = [NodePropertyStep(Globals.focus,
                                                                        "angle",
                                                                        oldFrameData[0],
                                                                        newFrameData[0]),
                                                       NodePropertyStep(Globals.focus,
                                                                        "radius",
                                                                        oldFrameData[1],
                                                                        newFrameData[1]),
                                                       NodePropertyStep(Globals.focus,
                                                                        "relRot",
                                                                        oldFrameData[2],
                                                                        newFrameData[2]),
                                                       NodePropertyStep(Globals.focus,
                                                                        "directMot",
                                                                        oldFrameData[3],
                                                                        newFrameData[3])]
                                    elif SET is self.kframeComponents:
                                        undoredolst = [KeyFramePropertyStep(Globals.selectedFrame,
                                                                            "angle",
                                                                            oldFrameData[0],
                                                                            newFrameData[0]),
                                                       KeyFramePropertyStep(Globals.selectedFrame,
                                                                            "radius",
                                                                            oldFrameData[1],
                                                                            newFrameData[1]),
                                                       KeyFramePropertyStep(Globals.selectedFrame,
                                                                            "relativeRotation",
                                                                            oldFrameData[2],
                                                                            newFrameData[2]),
                                                       KeyFramePropertyStep(Globals.selectedFrame,
                                                                            "curveType",
                                                                            oldFrameData[3],
                                                                            newFrameData[3]),
                                                       KeyFramePropertyStep(Globals.selectedFrame,
                                                                            "time",
                                                                            oldFrameData[4],
                                                                            newFrameData[4])]
                                    UndoRedo.push(undoredolst)
                                Globals.root.refresh()
        
    def update(self):
        if Globals.focus != None:
            self.updateComponentSet(self.nodeComponents)
        else:
            for butt in self.nodeComponents:
                butt.softReset()
                
        if Globals.selectedFrame != None:
            self.updateComponentSet(self.kframeComponents)
        else:
            for butt in self.kframeComponents:
                butt.softReset()
                
        for butt in self.buttons:
            if butt.collidePoint(*self.localCoords(mx,my)):
                butt.onHover()
            else:
                butt.offHover()
            butt.manualUpdate()

        for evt in self.inputs["events"]:
            if evt.type == MOUSEBUTTONDOWN:
                for butt in self.buttons:
                    if butt.collidePoint(*evt.pos):
                        butt.onClick()
                        
    def render(self,screen):
        screen.fill((200,200,200))
            
        
        
class NodeRightClickMenu(BasicRightClickMenu):
    def __init__(self,pos):
        super().__init__([pos[0],pos[1],70,150],"NodeRightClickMenu")
        
    def init(self):
        self.addButton(RightMenuButton("Insert Key Frame","insertkframe"))
        self.addButton(RightMenuButton("Copy Data","copyData"))
        self.addButton(RightMenuButton("Paste Data","pasteData"))
        self.addButton(RightMenuButton("Delete Node","delNode"))

    def buttonClicked(self,button_name):
        if button_name == "insertkframe":
            undoredolst = []
            for n in Globals.lassoed:
                xform = KeyFrame(n.angle,Globals.t,n.colour,n.radius)
                xform.relativeRotation = n.relRot
                if n.directMot:
                    xform.curveType = "Direct"    
                tmp = n.addTransform(xform)
                undoredolst.append(InsertKeyFrameStep(n,xform,tmp))
            Globals.selectedFrame = xform
            UndoRedo.push(undoredolst)
            Globals.updateKeyFrameEditor = True
        elif button_name == "copyData":
            if len(Globals.lassoed) == 1:
                Globals.errorMsg = "Node ID: %i Data Copied!"%Globals.lassoed[0].id
            else:
                Globals.errorMsg = "Unable to copy data of multiple lassoed Nodes!"
        elif button_name == "pasteData":
            if len(Globals.lassoed) == 1:
                Globals.errorMsg = "Data pasted into Node ID: %i!"%Globals.lassoed[0].id
            else:
                Globals.errorMsg = "Unable to paste data into multiple Nodes!"
        elif button_name == "delNode":
            undoredolst = []
            for n in Globals.lassoed:
                if n.root != None:
                    undoredolst.append(DelNodeStep(n,n.root))
                    n.removeSelf()
                else:
                    Globals.errorMsg = "Warning: Unable to Remove Root!"
            if len(undoredolst) > 0:
                UndoRedo.push(undoredolst)
            Globals.focus = None
class KeyFrameRightClickMenu(BasicRightClickMenu):
    def __init__(self,pos):
        super().__init__([pos[0],pos[1],70,100],"KeyFrameRightClickMenu")
        
    def init(self):
        self.addButton(RightMenuButton("Copy Data","copyData"))
        self.addButton(RightMenuButton("Paste Data","pasteData"))
        self.addButton(RightMenuButton("Delete KeyFrame","delkframe"))
        
    def buttonClicked(self,button_name):
        if button_name == "copyData":
            Globals.errorMsg = "KeyFrame Data Copied!"
        elif button_name == "pasteData":
            Globals.errorMsg = "Data Pasted into KeyFrame!"
        elif button_name == "delkframe":
            UndoRedo.push([DelKeyFrameStep(Globals.focus,
                                           Globals.highlightedFrame)])
            Globals.focus.removeTransform(Globals.highlightedFrame)
        
class TimeInput(IntegerInput):
    def datatype(self,text):
        i = int(text)
        if i < 0:
            return 0
        elif i > Globals.tLim:
            return Globals.tLim
        else:
            return i
    def setVal(self):
        super().setVal()
        Globals.focus.updateTransforms()

class RenderScriptInput(TextInput):
    def __init__(self,pointer,x,y):
        super().__init__([x,y,150,20],pointer,20)

    def setVal(self):
        super().setVal()
        if self.value != "":
            result = self.ptr.pointsTo().getVal().loadRenderScript()
            if result == "":
                self.ptr.pointsTo().getVal().validScript = True
            Globals.errorMsg = result
        else:
            Globals.errorMsg = ""
            self.ptr.pointsTo().getVal().validScript = False
UndoRedo.init(Globals)

interface = MainInterface()
interface.addWindow(EditorWindow([150,30,650,500]))
interface.addWindow(KeyFrameWindow([150,540,650,90]))
interface.addWindow(ToolbarWindow([15,30,120,600]))
interface.addWindow(PropertiesEditor([815,30,170,500]))

Globals.nodercmenu = NodeRightClickMenu([100,100]) #initialize
interface.addWindow(Globals.nodercmenu)
Globals.keyrcmenu = KeyFrameRightClickMenu([100,100]) #initialize
interface.addWindow(Globals.keyrcmenu)

myClock = time.Clock()
while running:
    eventQueue = []
    for evt in event.get():
        if evt.type == QUIT:
            running = False
        else:
            eventQueue.append(evt)
            
    mx,my = mouse.get_pos()
    mb = mouse.get_pressed()
    kb = key.get_pressed()
    interface.updateInputs(mx,my,mb,kb,eventQueue)
    interface.mainUpdate()
    interface.mainRender(screen)
    
    myClock.tick(60)
    display.flip()
quit()

