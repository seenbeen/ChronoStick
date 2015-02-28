def cross(p0,p1,p2):
    return (p1[0]-p0[0])*(p2[1]-p0[1])-(p2[0]-p0[0])*(p1[1]-p0[1])

'''def avg(lst,fn):
    x,y = 0,0
    for n in lst:
        x+=n[0]
        y+=n[1]
    n = len(lst)
    return [int(x/n),int(y/n)]'''

def withinPoly(pt,poly,boundingRect):
    '''Returns True if [x0,y0] is in polygon defined by [[x1,y1]...[xn,yn]]'''
    if not boundingRect.collidepoint(*pt):
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
