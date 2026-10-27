class AgentExemple:
    def __init__(self,environment,IDAgent):
        self.environment = environment
        self.IDAgent = IDAgent

        self.carte_mental = []
        self.armoire_mental = []
        
        self.nextMove = "ATTENDRE"

        self.infoDeBase = environment.get_initAgent_info()
    
    def updateState(self):
        """je sais pas encore exactement quoi mettre"""
        newinfo = self.environment.get_perception(self.IDAgent)
        # traiter newinfo pour changer d'état ou mettre à jour carte_mental si besoin

    def compute_NextMove(self):
        """met à jour nextMove selon état et position actuel"""
        self.nextMove = ["AVANCER","DROITE"]
