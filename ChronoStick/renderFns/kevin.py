#globals()["kevinPic"] = image.load("icon.png")
    
def render(self,screen,nodes):

    #for x in nodes.values():
    #    print("node%i = Node(%i,%i)\nnode%i.addChild(node%i)"%(x.id,x.x,x.y,x.getRoot().id,x.id))
    #print("------------------------------")
    #a = self.angle
    #x = self.renderCoords()[0]
    #y = self.renderCoords()[1]
    #tempPic = transform.rotate(globals()["kevinPic"],180-math.degrees(a))
    #screen.blit(tempPic,(x-tempPic.get_width()//2,
    #                     y-tempPic.get_height()//2))
    #draw.line(screen,(0,255,0),self.renderCoords(),nodes[21].renderCoords(),10)
    self.zProp = 10
    self._render(screen,(150,30))

    self.zProp = -30
    R = 110
    r = 40
    bladeScale = 2
    startCol = (0,105,255)
    endCol = (255,255,255)
    colourTransition = 1
    revPerCycle = 0.5
    distort = 1
    phaseshift = 0
    
    x0,y0 = self.renderCoords()
    innerPoints = []
    outerPoints = []
    incr = ((endCol[0]-startCol[0])/(10*colourTransition),
            (endCol[1]-startCol[1])/(10*colourTransition),
            (endCol[2]-startCol[2])/(10*colourTransition))
    t = (self.time)*revPerCycle/30*math.pi*2+phaseshift
    x1 = R*math.cos(t/distort)
    y1 = r*math.sin(t/distort)
    x2 = int(R*math.cos(t)*bladeScale)
    y2 = int(r*math.sin(t)*bladeScale)
    innerPoints.append([x0+x1,y0+y1])
    outerPoints.append([x0+x2,y0+y2])
    for i in range(1,10*colourTransition):
        t = ((self.time-i/colourTransition)*revPerCycle/30*math.pi*2+phaseshift)
        x1 = R*math.cos(t/distort)
        y1 = r*math.sin(t/distort)
        c = list(map(int,(startCol[0]+incr[0]*i,
             startCol[1]+incr[1]*i,
             startCol[2]+incr[2]*i)))
        x2 = int(R*math.cos(t)*bladeScale)
        y2 = int(r*math.sin(t)*bladeScale)
        innerPoints.append([x0+x1,y0+y1])
        outerPoints.append([x0+x2,y0+y2])
        draw.polygon(screen,c,[innerPoints[-2],innerPoints[-1],
                               outerPoints[-1],outerPoints[-2]])
    #draw.lines(screen,,False,points,5)
    #draw.circle(screen,(0,0,0),(x,y),15)
    #draw.line(screen,(0,0,255),self.renderCoords(),nodes[17].renderCoords(),5)
    
    #draw.ellipse(screen,(255,0,0),(x-110,y-40,220,80),5)
    #image.save(screen.subsurface([150,30,650,500]),"deepSwing/deepSwing%i.png"%self.time)
