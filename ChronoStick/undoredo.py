from pointer import *


class UndoRedo:
    undoStack = []
    redoStack = []
    Globals = None
    
    def init(GLOBALS):
        UndoRedo.Globals = GLOBALS

    def Validate():
        if UndoRedo.Globals == None:
            print("Warning: UndoRedo module not initiated!")
            return False
        return True
    
    def undo():
        if UndoRedo.Validate():    
            if len(UndoRedo.undoStack) > 0:
                step = UndoRedo.undoStack.pop()
                for s in step:
                    s.undo()
                UndoRedo.redoStack.append(step)

    def redo():
        if UndoRedo.Validate():    
            if len(UndoRedo.redoStack) > 0:
                step = UndoRedo.redoStack.pop()
                for s in step:
                    s.redo()
                UndoRedo.undoStack.append(step)

    def push(step):
        if UndoRedo.Validate():    
            UndoRedo.undoStack.append(step)
            UndoRedo.redoStack = []

class UndoRedoStep:
    def __init__(self,Globals):
        self.Globals = Globals
        pass
    def undo(self):
        pass
    def redo(self):
        pass

class KeyFramePropertyStep:
    def __init__(self,frame,prop,undoVal,redoVal):
        self.ptr = Pointer(frame,prop)
        self.undoVal = undoVal
        self.redoVal = redoVal
        self.frame = frame
    def undo(self):
        self.ptr.setVal(self.undoVal)
        UndoRedo.Globals.selectedFrame = self.frame
        UndoRedo.Globals.focus = self.frame.boundNode

    def redo(self):
        self.ptr.setVal(self.redoVal)
        UndoRedo.Globals.selectedFrame = self.frame
        UndoRedo.Globals.focus = self.frame.boundNode

class NodePropertyStep:
    def __init__(self,node,prop,undoVal,redoVal):
        self.ptr = Pointer(node,prop)
        self.undoVal = undoVal
        self.redoVal = redoVal
        self.node = node
        
    def undo(self):
        self.ptr.setVal(self.undoVal)
        UndoRedo.Globals.focus = self.node

    def redo(self):
        self.ptr.setVal(self.redoVal)
        UndoRedo.Globals.focus = self.node

class DelNodeStep:
    def __init__(self,node,parent):
        self.parent = parent
        self.node = node
    def undo(self):
        self.parent.children.append(self.node)
        UndoRedo.Globals.focus = self.node
    def redo(self):
        self.node.removeSelf()
        if UndoRedo.Globals.focus != None:
            if UndoRedo.Globals.focus.id == self.node.id:
                UndoRedo.Globals.focus = None
                UndoRedo.Globals.curTool = "selectorTool"
class ExtrudeStep:
    def __init__(self,node,parent):
        self.parent = parent
        self.node = node
    def undo(self):
        self.node.removeSelf()
        if UndoRedo.Globals.focus != None:
            if UndoRedo.Globals.focus.id == self.node.id:
                UndoRedo.Globals.focus = None
                UndoRedo.Globals.curTool = "selectorTool"
    def redo(self):
        self.parent.children.append(self.node)
        UndoRedo.Globals.focus = self.node

class DelKeyFrameStep:
    def __init__(self,node,frame):
        self.node = node
        self.frame = frame
    def undo(self):
        self.node.addTransform(self.frame)
        UndoRedo.Globals.focus = self.node
        UndoRedo.Globals.selectedFrame = self.frame
    def redo(self):
        self.node.removeTransform(self.frame)
        if UndoRedo.Globals.selectedFrame != None:
            if UndoRedo.Globals.selectedFrame.id == self.frame.id:
                UndoRedo.Globals.selectedFrame = None
        
class InsertKeyFrameStep:
    def __init__(self,node,frame,oldframe):
        self.node = node
        self.frame = frame
        self.oldframe = oldframe
        
    def undo(self):
        self.node.removeTransform(self.frame)
        if self.oldframe != None:
            self.node.addTransform(self.oldframe)
        UndoRedo.Globals.updateKeyFrameEditor = True
        if UndoRedo.Globals.selectedFrame != None:
            if UndoRedo.Globals.selectedFrame.id == self.frame.id:
                UndoRedo.Globals.selectedFrame = None
                
    def redo(self):
        self.node.addTransform(self.frame)
        UndoRedo.Globals.focus = self.node
        UndoRedo.Globals.selectedFrame = self.frame
        UndoRedo.Globals.updateKeyFrameEditor = True
