from MouvementDansArmoire import *

class AgentExemple:
    def __init__(self,environment,IDAgent):
        self.environment = environment
        self.IDAgent = IDAgent

        self.carte_mental = []
        self.armoire_mental = []
        self.newinfo = {}
        #etats = EXPLORER, boucle(DICTIONNAIRE, ARMOIRE, OBJET, LIVRAISON)  
        self.etat = "EXPLORER"
        self.is_etatfinish = False

        self.actionMaker =  # il doit etre a explorer
        self.nextMove = ["CHERCHER","DROITE"]
        
        # Variable de test Env._handleAction
        self.futurNextMove = [
            ["CHERCHER","DROITE"],
            ["Prendre",None]
        ]
        self.i = 0

        self.infoDeBase = environment.get_initAgent_info()
    
    def updateState(self):
        """je sais pas encore exactement quoi mettre"""
        self.newinfo = self.environment.get_perception(self.IDAgent)

        if self.is_etatfinish:
            self.nextState()
            self.is_etatfinish = False
        # traiter newinfo pour changer d'état ou mettre à jour carte_mental si besoin
        # met à jour la map
        # si  

    def compute_NextMove(self):
        """met à jour nextMove selon état et ses infos actuel"""
        #TODO ici 
        match self.etat:
            case "EXPLORER":
                pass #functionExplorer() explore la map 
            case "DICTIONNAIRE":
                if 'D' in self.newinfo['perception'].values():
                    pass #functionDictionnaire() si à coter du dico return action consulter , sinon action Avancer qui se rapproche du dico
            case "ARMOIRE":
                if 'A' in self.newinfo['perception'].values(): # si à coter de l'armoire
                    self.actionMaker = MouvementDansArmoire(self, self.newinfo['posTerrain'], emotion, intensite)
                else: # sinon action Avancer qui se rapproche de l'armoire
                    pass 
            case "OBJET":
                self.nextMove = self.actionMaker.nextAction()
            case "LIVRAISON":
                pass #functionLivraison() si à coter de recepteur return action Donner, sinon action Avancer se rapprocher du recepteur
        # foutre le résultat dans self.nextMove ( on pourra changer si besoin)

        self.nextMove = self.futurNextMove[self.i]
        self.i = (self.i + 1) % 2