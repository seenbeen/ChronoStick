from pygame import *

screen = display.set_mode((800,600))

running = True
recording = False
pts = []
pt = [0,0]

clock = time.Clock()

def cross(p0,p1,p2):
    return (p1[0]-p0[0])*(p2[1]-p0[1])-(p2[0]-p0[0])*(p1[1]-p0[1])

def withinPoly(pt,poly,boundingRect):
    '''Returns True if [x0,y0] is in polygon defined by [[x1,y1]...[xn,yn]]'''
    if not boundingRect.collidepoint(*pt):
        print ("insta ded XD")
        return False
    poly.append(poly[0][::])
    wn = 0
    for i in range(len(poly)-1):
        if (poly[i][1] <= pt[1]):
            if (poly[i+1][1] > pt[1]):
                if (cross(poly[i],poly[i+1],pt) > 0):
                    wn+=1;
        else:
            if (poly[i+1][1] <= pt[1]):
                if (cross(poly[i],poly[i+1],pt) < 0):
                    wn-=1;
    return wn != 0

brect = [800,600,0,0]

while running:
    for evt in event.get():
        if evt.type == QUIT:
            running = False
        elif evt.type == MOUSEBUTTONDOWN:
            if evt.button == 1:
                pt = evt.pos
            elif evt.button == 3:
                recording = True
                pts = []
                brect = [800,600,0,0]
            elif evt.button == 2:
                rkt = Rect(brect[0],brect[1],
                        brect[2]-brect[0],
                        brect[3]-brect[1])
                print (withinPoly(pt,pts,rkt))
        elif evt.type == MOUSEBUTTONUP:
            if evt.button == 3:
                recording = False
                print (len(pts))
    screen.fill((0,0,0))
    if recording:
        mpos = mouse.get_pos()
        pts.append(mpos)
        if mpos[0] > brect[2]:
            brect[2] = mpos[0]
        if mpos[0] < brect[0]:
            brect[0] = mpos[0]
        if mpos[1] > brect[3]:
            brect[3] = mpos[1]
        if mpos[1] < brect[1]:
            brect[1] = mpos[1]
            
    if len(pts) > 1:
        draw.polygon(screen,(255,255,255),pts,1)
    draw.circle(screen,(255,255,255),pt,5)
    draw.rect(screen,(0,255,0),(brect[0],brect[1],
                                brect[2]-brect[0],
                                brect[3]-brect[1]),2)
    display.flip()
    clock.tick(60)
quit()
