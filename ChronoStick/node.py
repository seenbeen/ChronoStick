from pygame import *
import math
import cstickmath

class KeyFrame:
    IDS = 0
    def __init__(self,angle,time,colour,radius = 0):
        self.angle = angle
        self.time = time
        self.colour = colour
        self.radius = radius
        self.id = KeyFrame.IDS
        KeyFrame.IDS += 1
        self.relativeRotation = True
        self.curveType = "Smooth"
        self.boundNode = None
        
    def interpolate(self,frame,t,node):
        #implementation of calculating an interpolation
        #note that this can be altered at any time to support
        #any additional interpolation features in the future
        
        deltaTime = frame.time-self.time
        elapsedTime = t-self.time
        deltaAng = frame.angle-self.angle
        oriAng = self.angle
        
        if elapsedTime > 0 and frame.id != self.id:
            k = elapsedTime/deltaTime
        else:
            k = 0

        colour = list(map(lambda x,y: int(x+(y-x)*k),
                            self.colour,
                            frame.colour))

        #calculate interpolation based on curve type
        relPeriod = 0
        finalAng = oriAng
        if self.relativeRotation == frame.relativeRotation:
            if self.curveType == "Smooth":
                node.directMot = False
                period = math.pi/2*(k)

                L = deltaAng/(math.pi/2)
                
                dx = self.radius*math.cos(period)
                dy = frame.radius*math.sin(period)
                
                actualAng = math.atan2(dy,dx)
                
                node.radius = math.hypot(dx,dy)

                finalAng = oriAng+actualAng*L
                    
            elif self.curveType == "Direct":
                node.directMot = True
                x1 = self.radius*math.cos(self.angle)
                y1 = self.radius*math.sin(self.angle)
                x2 = frame.radius*math.cos(frame.angle)
                y2 = frame.radius*math.sin(frame.angle)
                x = x1+k*(x2-x1)
                y = y1+k*(y2-y1)
                actualAng = cstickmath.vectAngle([x1,y1],[x,y])
                node.radius = math.hypot(x,y)
                finalAng = oriAng+actualAng

        #set our new settings
        node.relRot = self.relativeRotation
        node.rotateTo(finalAng)#-offset)
        node.colour = colour
        
class Node:
    IDS = 0
    def isRoot(self):
        return self.root == None
    
    def __init__(self,x,y):
        self.id = Node.IDS
        Node.IDS += 1

        self.x = x
        self.y = y

        self.root = None
        self.children = []
        self.angle = math.atan2(y,x)

        #interp factors
        self.radius = math.hypot(x,y)
        self.colour = (0,0,0)
        self.thickness = 2
        #self.alterAngle = 0
        
        self.transforms = [KeyFrame(self.angle,0,(0,0,0),self.radius)]
        self.transforms[0].boundNode = self
        #Note: extraData doesn't alter node properties;
        #      most of these are used by the editor to
        #      track details for key-frame adding
        self.extraData = {}
        self.relRot = True
        self.directMot = False
        self.renderScript = ""
        self.validScript = False
        self.zProp = 0 #used to determine which to render first

        self.extraData["renderCoords"] = (0,0)
        
    def fetchGlobalAngle(self):
        return math.atan2(self.y,self.x)

    def fetchLocalAngle(self):
        root = self.getRoot()
        return math.atan2(self.y-root.y,self.x-root.x)
    
    def fetchGlobalRad(self):
        return math.hypot(self.x,self.y)

    """rotateTo takes in an angle and rotates this node about its parent
       such that the angle made by its grandparent, parent and itself is
       equal to ang"""
    def rotateTo(self,ang):
        self.angle = ang
        self.refresh()

    def getRoot(self):
        #All root nodes have a parent as the origin. :)
        if self.root == None:
            return ORIGIN
        return self.root
    
    def refresh(self):
        root = self.getRoot()

        root_root = root.getRoot()

        if self.relRot:
            vect1 = (root_root.x-root.x,root_root.y-root.y)
            vect2 = (-root.x,-root.y)
            
            a = self.angle-cstickmath.vectAngle(vect1,vect2)+math.pi#-self.alterAngle
            
            root_dist = root.fetchGlobalRad()
            
            tx = root_dist+self.radius*math.cos(a)
            ty = self.radius*math.sin(a)

            #rotate back into editor's frame of ref
            origA = math.atan2(ty,tx) #initial angle
            origR = math.hypot(tx,ty) #distance from origin

            #localA used to rotate point back into the editor's frame of ref
            localA = root.fetchGlobalAngle()
            
            self.x = origR*math.cos(origA+localA)
            self.y = origR*math.sin(origA+localA)
        else:
            self.x = root.x+self.radius*math.cos(self.angle)
            self.y = root.y+self.radius*math.sin(self.angle)
            
        for child in self.children:
            child.refresh()

    def nonRelativeShift(self,t0,t1):
        shift = 0
        for i in range(len(self.transforms)):
            if t0 < self.transforms[i].time:
                if self.transforms[i-1].time > t1:
                    continue
                
                deltaAng = self.transforms[i].angle - self.transforms[i-1].angle
                deltaTime = self.transforms[i].time - self.transforms[i-1].time
                if deltaTime == 0:
                    before = 0
                    after = 0
                else:
                    before = (max(self.transforms[i-1].time,t0)-self.transforms[i-1].time)/deltaTime
                    after = (min(self.transforms[i].time,t1)-self.transforms[i-1].time)/deltaTime

                if self.transforms[i-1].curveType == "Direct":
                    curFrame = self.transforms[i]
                    pastFrame = self.transforms[i-1]
                    x1 = pastFrame.radius*math.cos(pastFrame.angle)
                    y1 = pastFrame.radius*math.sin(pastFrame.angle)
                    x2 = curFrame.radius*math.cos(curFrame.angle)
                    y2 = curFrame.radius*math.sin(curFrame.angle)
                    
                    x_0 = x1+before*(x2-x1)
                    y_0 = y1+before*(y2-y1)
                    x = x1+after*(x2-x1)
                    y = y1+after*(y2-y1)
                    
                    actualAng = cstickmath.vectAngle([x_0,y_0],[x,y])

                else:
                    L = deltaAng/(math.pi/2)
                    
                    
                    p0 = math.pi/2*before
                    p1 = math.pi/2*after
                    
                    dx_1 = self.transforms[i-1].radius*math.cos(p0)
                    dy_1 = self.transforms[i].radius*math.sin(p0)

                    dx_2 = self.transforms[i-1].radius*math.cos(p1)
                    dy_2 = self.transforms[i].radius*math.sin(p1)
                    
                    actualAng = (math.atan2(dy_2,dx_2)-math.atan2(dy_1,dx_1))*L
                    

                shift += actualAng
                
        return shift                

    """addChild consumes a child node to be added and makes it a child
       node of this node, setting the child's parent (root) to this node"""
    
    def addChild(self,child):
        self.children.append(child)
        child.root = self
        
        root = self.getRoot()

        vect1 = [root.x-self.x,root.y-self.y]
        vect2 = [child.x-self.x,child.y-self.y]
        child.angle = cstickmath.vectAngle(vect1,vect2)

        child.radius = math.hypot(*vect2)
        child.transforms = [KeyFrame(child.angle,0,self.colour,child.radius)]

    #insert xform in chronological order using sorted-insert
    # assume that initial transform list is empty or in order
    # Note: If the xform shares the same time as a previous xform,
    #       xform overrides, and previous xform is returned
    
    def addTransform(self,xform):
        xform.boundNode = self
        for i in range(len(self.transforms)):
            if self.transforms[i].time == xform.time:
                temp = self.transforms[i]
                self.transforms = self.transforms[:i]+[xform]+self.transforms[i+1:]
                return temp
            elif self.transforms[i].time > xform.time:
                self.transforms = self.transforms[:i]+[xform]+self.transforms[i:]
                return None
        self.transforms.append(xform)
        
    def removeTransform(self,xform):
        xform.boundNode = None
        for i in range(len(self.transforms)):
            if self.transforms[i].id == xform.id:
                del(self.transforms[i])
                return
        print("Warning: Trying to Remove Non-Existent KeyFrame")
        
    def updateTransforms(self):
        for i in range(len(self.transforms)-1):
            if self.transforms[i].time > self.transforms[i+1].time:
                xform = self.transforms[i]
                self.transforms = self.transforms[:i]+self.transforms[i+1:]
                self.addTransform(xform)
                return
        
    """removeChild uses O(n) to remove a given child from its children
       Note that removeChild returns a warning if the child is not found."""
    def removeChild(self,child):
        for i in range(len(self.children)):
            if self.children[i].id == child.id:
                del(self.children[i])
                return
        print("Warning: Attempting to remove non-existent child with id",child.id)


    """removeSelf removes this node from the tree it's a part of.
        Children of this node will be assigned as children of this
        node's parent."""
    def removeSelf(self):
        self.root.removeChild(self)
            
        
    def setTime(self,time):
        for i in range(len(self.transforms)-1):
            if self.transforms[i].time <= time and time <= self.transforms[i+1].time:
                self.transforms[i].interpolate(self.transforms[i+1],time,self)
                break
        else:
            x = 0
            if abs(time-self.transforms[0].time) > abs(time-self.transforms[-1].time):
                x = -1
            self.transforms[x].interpolate(self.transforms[x],
                                           time,self)
            
        for child in self.children:
            child.setTime(time)
        self.time = time

    def getKeyFrameAtTime(self,time):
        for i in range(len(self.transforms)-1):
            if self.transforms[i].time <= time and time <= self.transforms[i+1].time:
                break
        else:
            i = 0
            if abs(time-self.transforms[0].time) > abs(time-self.transforms[-1].time):
                i = -1

        return self.transforms[i]

    def getOnion(self,lst):
        tmp = [self.displayCoords(),[]]
        for c in self.children:
            tmp[1].append(c.displayCoords())
        lst.append(tmp)
        for c in self.children:
            c.getOnion(lst)
        
    def displayCoords(self):
        """Returns local integer coords. Note: This is LOCAL coords, not Global!"""
        return (int(self.x),int(self.y))

    def renderCoords(self):
        return self.extraData["renderCoords"]
    
    #this render just shows node family relationships
    def _render(self,screen,offset = (0,0),showNode = True):
        p1 = list(map(lambda x,y: x+y,self.displayCoords(),offset))
        for child in self.children:
            p2 = list(map(lambda x,y: x+y,child.displayCoords(),offset))
            draw.line(screen,child.colour,p1,p2,4)
            draw.line(screen,(255,255,255),p1,p2,1)
        for child in self.children:
            child._render(screen,offset,showNode)
        if showNode:
            col = (255,0,0)
            if self.root == None:
                col = (255,0,255)
            draw.circle(screen,col,p1,5)

    def loadRenderScript(self):
        try:
            tmp = open(self.renderScript)
            exec(tmp.read())
            self.render = locals()["render"]
            tmp.close()
            return ""
        except Exception as err:
            return "Error loading Script:"+str(err)
                       
    def render(self,screen,nodes):
        pass

    def collideMouse(self,mx,my,within = 5):
        if math.hypot(self.x-mx,self.y-my) <= within:
            return self
        else:
            x = None
            for child in self.children:
                x = child.collideMouse(mx,my)
                if x != None:
                    break
            
            return x #suppose the mouse lands on nothing

    def grabChildren(self,lst):
        lst.append(self)
        for child in self.children:
            child.grabChildren(lst)
        return lst

ORIGIN = Node(0,0)
