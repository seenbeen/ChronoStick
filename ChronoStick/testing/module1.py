def derpDerp(der):
    der.troll()

class Der:
    lol = None

class py:
    def troll(self):
        print(Der.lol)
    def load(self):
        tmp = open("testFunction.txt","r")
        exec(tmp.read())
        tmp.close()
        self.render = locals()["render"]
        
    def render(self):
        print ("lolol")
        
