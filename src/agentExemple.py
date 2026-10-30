from MouvementDansArmoire import *
from Explorer import Explorer

class AgentExemple:
    def __init__(self,environment,IDAgent):
        self.environment = environment
        self.IDAgent = IDAgent

        self.carte_mental = []

        self.infoDeBase = environment.get_initAgent_info()

        self.newinfo = {}
        #etats = EXPLORER, boucle(DICTIONNAIRE, ARMOIRE, OBJET, LIVRAISON)  
        self.etat = "EXPLORER"
        self.is_etatfinish = False

        self.requete = self.environment.get_NextDemande(self.IDAgent)
        if self.requete == None:
            self.etat = None
        print(self.requete)

        #self.actionMaker = Explorer(self.infoDeBase["tailleCarte"])
        self.nextMove = ["ATTENDRE",""]

        self.infoDeBase = environment.get_initAgent_info()

    def nextState(self) :
            if self.etat == "EXPLORER" :
                self.etat = "DICTIONNAIRE"
            elif self.etat == "DICTIONNAIRE" :
                self.etat = "ARMOIRE"
            elif self.etat == "ARMOIRE" :
                self.etat = "OBJET"
            elif self.etat == "OBJET" :
                self.etat = "LIVRAISON"
            elif self.etat == "LIVRAISON" :
                self.etat = "DICTIONNAIRE" 
            else:
                self.etat = None

    def updateState(self):
        """je sais pas encore exactement quoi mettre"""
        self.self.newinfo = self.environment.get_perception(self.IDAgent)

        if self.is_etatfinish:
            self.nextState()
            self.is_etatfinish = False

        self.actionMaker.updateState()
        # traiter newinfo pour changer d'état ou mettre à jour carte_mental si besoin
        # met à jour la map
        # si  

    def compute_NextMove(self):
        """met à jour nextMove selon état et ses infos actuel"""
        #TODO ici 
        match self.etat:
            case "EXPLORER":
                self.nextMove = self.actionMaker.functionExplorer(self.newinfo["posTerrain"], self.newinfo)
                self.is_etatfinish = self.actionMaker.is_finish 
                self.carte_mental = self.actionMaker.carte_mental
            case "DICTIONNAIRE":
                if 'D' in self.newinfo['perception'].values(): # si à coter du dictionnaire
                    self.nextMove = ["CONSULTER", ""]
                    self.is_etatfinish = True
                else: # sinon action Avancer qui se rapproche de l'armoire
                    pass
            case "ARMOIRE":
                if 'A' in self.newinfo['perception'].values(): # si à coter de l'armoire
                    self.actionMaker = MouvementDansArmoire(self, self.newinfo['posTerrain'], self.newinfo['InfoDemande'][1][1], self.newinfo['InfoDemande'][1][0])
                    self.is_etatfinish = True
                else: # sinon action Avancer qui se rapproche de l'armoire
                    pass 
            case "OBJET":
                self.nextMove = self.actionMaker.nextAction()
                self.is_etatfinish = self.actionMaker.repli != None
            case "LIVRAISON":
                if self.requete["resident"] in self.newinfo['perception'].values(): # si à coter de recepteur return action Donner
                    self.nextMove = ["DONNER", ""]
                    self.is_etatfinish = True
                    self.environment.get_NextDemande(self.IDAgent)
                else: # sinon action Avancer se rapprocher du recepteur
                    pass