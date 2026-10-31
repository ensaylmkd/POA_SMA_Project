from MouvementDansArmoire import *
from MouvementDansMap import *
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

        self.infoDeBase = environment.get_initAgent_info()

        self.actionMaker = Explorer(self, self.infoDeBase["tailleCarte"])
        self.nextMove = ["ATTENDRE",""]

    def nextState(self) :
        if self.etat == "EXPLORER" :
            self.etat = "DICTIONNAIRE"
        elif self.etat == "DICTIONNAIRE" :
            self.etat = "ARMOIRE"
        elif self.etat == "ARMOIRE" :
            self.etat = "LIVRAISON"
        elif self.etat == "LIVRAISON" and self.requete is not None:
            self.etat = "DICTIONNAIRE" 
        else:
            self.etat = ""
            self.nextMove = ["ATTENDRE",""]

    def updateState(self):
        """je sais pas encore exactement quoi mettre"""
        self.newinfo = self.environment.get_perception(self.IDAgent)

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
        print(self.etat)
        match self.etat:
            case "EXPLORER":
                self.nextMove = self.actionMaker.nextAction()
                self.carte_mental = self.actionMaker.carte_mental
                self.is_etatfinish = self.actionMaker.is_finish 
            case "DICTIONNAIRE":
                if 'D' in self.newinfo['perception'].values(): # si à coter du dictionnaire
                    self.nextMove = ["CONSULTER", ""]
                    self.is_etatfinish = True
                else: # sinon action Avancer qui se rapproche de l'armoire
                    self.actionMaker = MouvementDansMap(self, self.newinfo['posTerrain'], self.infoDeBase['dictionnairePos'], self.carte_mental)
                    self.nextMove = self.actionMaker.nextAction()
            case "ARMOIRE":
                if 'A' in self.newinfo['perception'].values(): # si à coter de l'armoire
                    if not isinstance(self.actionMaker, MouvementDansArmoire):
                        self.actionMaker = MouvementDansArmoire(self, self.newinfo['posCasier'], self.newinfo['InfoDemande'][1], self.newinfo['InfoDemande'][0])
                    self.nextMove = self.actionMaker.nextAction()
                    self.is_etatfinish = self.actionMaker.repli != None
                else: # sinon action Avancer qui se rapproche de l'armoire
                    self.actionMaker = MouvementDansMap(self, self.newinfo['posTerrain'], self.infoDeBase['armoirePos'], self.carte_mental)
                    self.nextMove = self.actionMaker.nextAction()
            case "LIVRAISON":
                for r in self.infoDeBase['residents']:
                    if r['id'] == self.requete['resident']:
                        posResident = r['position']
                if 'P' in self.newinfo['perception'].values() and dist(self.newinfo['posTerrain'], posResident) == 1: # si à coter de recepteur return action Donner
                    self.nextMove = ["DONNER", ""]
                    self.requete = self.environment.get_NextDemande(self.IDAgent)
                    self.is_etatfinish = True
                else: # sinon action Avancer se rapprocher du recepteur
                    self.actionMaker = MouvementDansMap(self, self.newinfo['posTerrain'], posResident, self.carte_mental)
                    self.nextMove = self.actionMaker.nextAction()

def dist(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])