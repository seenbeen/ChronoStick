#globals()["testPic"] = image.load("testPicture.png")
def render(self,screen,nodes):
    draw.circle(screen,(0,255,255),self.renderCoords(),20)
    #draw.line(screen,(0,0,0),self.renderCoords(),nodes[3].renderCoords(),13)
    #draw.line(screen,(0,255,0),self.renderCoords(),nodes[3].renderCoords(),10)
    #screen.blit(globals()["testPic"],self.renderCoords())
    #self.zProp = 1
