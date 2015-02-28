def createSpline(t1,r1,t2,r2):
    a = 2*(r2-r1)/((t1-t2)**2)
    h = (t2+t1)/2
    return "Plot[Piecewise[{{%.2f(x-%.2f)^2+%.2f, 0<= x <= %.2f}, {-%.2f(x-%.2f)^2+%.2f, %.2f < x <= %.2f}}], {x, %.2f, %.2f}]"%(a,t1,r1,h,a,t2,r2,h,t2,t1,t2)

def splineCurve(t1,r1,t2,r2,t):
    h = (t2+t1)/2
    a = 2*(r2-r1)/((t1-t2)**2)
    if t <= h:
        return a*(t-t1)**2+r1
    else:
        return -a*(t-t2)**2+r2

from pygame import *
import math

running = True
screen = display.set_mode((800,600))

def drawSpline(t1,r1,t2,r2):
    if t1 == t2:
        print ("Error: t2 must be greater than t1")
        return
    
    p0 = (t1,r1)
    for i in range(t1+1,t2):
        p1 = (i,int(splineCurve(t1,r1,t2,r2,i)))
        draw.line(screen,(255,255,255),p0,p1)
        p0 = p1

def drawSplineCurve(pointList):
    if len(pointList) < 2:
        print ("There must be at least 2 points to make a curve!")
        return
    p0 = pointList[0]
    for i in range(1,len(pointList)):
        p1 = pointList[i]
        drawSpline(p0[0],p0[1],p1[0],p1[1])
        p0 = p1
    
drawSplineCurve([[0,100],[100,0],[300,500],[450,452]])

##screen.set_at((400,300),(0,255,0))
##a = 0#-math.pi/6
##r1 = 20
##r2 = 50
##k = 1
##lst = []
##for i in range(0,100):
##    period = math.pi/2*(i/100)
##    dx = r1*math.cos(period)
##    dy = r2*math.sin(period)
##    r = math.hypot(dx,dy)
##    ang = math.atan2(dy,dx)
##    
##    lst.append((400+int(r*math.cos(a+ang*k)),300+int(r*math.sin(a+ang*k))))
##draw.lines(screen,(255,255,255),False,lst)
    
while running:
    for evt in event.get():
        if evt.type == QUIT:
            running = False
    
    display.flip()

quit()
