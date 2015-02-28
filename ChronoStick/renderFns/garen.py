globals()["garen"] = image.load("garen.png")
w = globals()["garen"].get_width()//2
h = globals()["garen"].get_height()//2
globals()["garen"] = transform.scale(globals()["garen"],(w,h))    
def render(self,screen,nodes):
    x,y = self.renderCoords()
    lul = transform.rotate(globals()["garen"],
                           270-math.degrees(self.fetchLocalAngle()))
    w = lul.get_width()/2
    h = lul.get_height()/2

    screen.blit(lul,(x-w,y-h))
    
    #image.save(screen.subsurface([150,30,650,500]),"deepSwing/deepSwing%i.png"%self.time)
