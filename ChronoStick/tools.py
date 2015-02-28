import math

def avgPt(lst):
    x,y = 0,0
    for n in lst:
        p = n.displayCoords()
        x+=p[0]
        y+=p[1]
    n = len(lst)
    return [int(x/n),int(y/n)]

def projMag(v1,v2):
    return (v1[0]*v2[0]+v1[1]*v2[1])/math.hypot(*v2)


def difference(l1,l2):
    for i in range(len(l1)):
        if l1[i] != l2[i]:
            return True
    return False
