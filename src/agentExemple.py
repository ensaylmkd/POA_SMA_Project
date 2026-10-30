class AgentExemple:
    def __init__(self,environment,IDAgent):
        self.environment = environment
        self.IDAgent = IDAgent

        self.carte_mental = []
        self.armoire_mental = []
        
        self.nextMove = ["CHERCHER","DROITE"]
        
        # Variable de test Env._handleAction
        self.futurNextMove = [
            ["AVANCER","Droite"],
            ["AVANCER","Droite"],
            ["Chercher","DROITE"],
            ["AVANCER","HAut"],
            ["AVANCER","HAut"],
            ["AVANCER","Droite"],
            ["AVANCER","HAut"],
            ["AVANCER","HAut"],
            ["AVANCER","HAut"],
            ["Prendre",None],
            ["Chercher","DROITE"],
            ["AVANCER","HAut"],
            ["AVANCER","HAut"]
        ]
        self.i = 0

        self.infoDeBase = environment.get_initAgent_info()
    
    def updateState(self):
        """je sais pas encore exactement quoi mettre"""
        newinfo = self.environment.get_perception(self.IDAgent)
        # traiter newinfo pour changer d'état ou mettre à jour carte_mental si besoin

    def compute_NextMove(self):
        """met à jour nextMove selon état et position actuel"""
        self.nextMove = self.futurNextMove[self.i]
        self.i = (self.i + 1) 
