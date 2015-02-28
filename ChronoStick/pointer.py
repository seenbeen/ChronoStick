import inspect

class Pointer():
    def __init__(self,a,attr):
        self.a = a
        self.attr = attr
        
    def setVal(self,val):
        if inspect.isclass(self.a):
            print ("Error: Unable to modify static class variable")
            return
        
        if isinstance(self.a,Pointer):
            self.a.getVal().__setattr__(self.attr,val)
        else:
            self.a.__setattr__(self.attr,val)
            
    def pointsTo(self):
        return self.a
    
    def _getVal(self,a,attr):
        if a == None: #handling null-pointers C:
            return None
        if inspect.isclass(a):
            return a.__getattribute__(a,attr)
        else:
            return a.__getattribute__(attr)

    def getVal(self):
        if isinstance(self.a,Pointer):
            return self._getVal(self.a.getVal(),self.attr)
        else:
            return self._getVal(self.a,self.attr)
