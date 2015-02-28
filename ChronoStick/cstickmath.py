import math

def vectAngle(vect1,vect2):
    #fancy maff; dot gives ratio of cos; cross gives ratio of sin    
    dot = vect1[0]*vect2[0]+vect1[1]*vect2[1]
    cross = vect1[0]*vect2[1]-vect1[1]*vect2[0]

    #in the case of a zero vector, assume a root angle of pi
    if cross == 0 and dot == 0:
        return math.pi
    
    return math.atan2(cross,dot)%(2*math.pi)
    #modulo required to fix wraparound
    #(atan2 gives [-pi,pi] when [0,2pi] is desired)
