class IActionMaker:
    def __init__(self,agent):
        self.agent = agent
    
    def updateState(self):
        return
    
    def nextAction(self):
        return ["ATTENDRE",None]
    
    def is_finish(self):
        return True