from src.ActionMaker.MouvementDansArmoire import *
from src.ActionMaker.MouvementDansMap import *
from src.ActionMaker.Explorer import Explorer

class AgentExemple:
    def __init__(self,environment,IDAgent):
        self.environment = environment
        self.IDAgent = IDAgent

        self.infoDeBase = environment.get_initAgent_info()

        self.newinfo = {}
        #etats = EXPLORER, boucle(DICTIONNAIRE, ARMOIRE, OBJET, LIVRAISON)  
        self.etat = "EXPLORER"
        self.is_etatfinish = False
        self.on = True
        self.errorMsg = None

        self.innaccessiblePlace = []
        self.nextMove = ["ATTENDRE",""]


        self.infoDeBase = environment.get_initAgent_info()
        self.actionMaker = Explorer(self, self.infoDeBase["tailleCarte"])      
        self.requete = self.environment.get_NextDemande(self.IDAgent)
        if self.requete == None:
            self.on = False
            self.errorMsg = "pas de requète"

    def nextState(self) :
        if self.etat == "EXPLORER":
            self.innaccessiblePlace = self.InnaccessiblePlace()
            if not self.isPossibleToDelivery():
                self.on = False
            self.checkRequest()
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

        if self.requete is None or not self.on:
            self.requete = self.environment.get_NextDemande(self.IDAgent)
            self.checkRequest()
            return

        if self.is_etatfinish and self.on:
            self.nextState()
            self.is_etatfinish = False
        
        self.actionMaker.updateState()
    
    def compute_NextMove(self):
        """met à jour nextMove selon état et ses infos actuel"""
        if self.requete is None or not self.on:
            self.nextMove = ["ATTENDRE",""]
        else:
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
                    r = self.environment.get_residentInfoByRID(self.requete['resident'])
                    if r is None :
                        self.nextMove = ["ATTENDRE", ""]
                        self.requete = None 
                        self.is_etatfinish = True
                        self.errorMsg = "Le résident n'existe pas"
                    
                    else:
                        posResident = r["position"]
                        if 'P' in self.newinfo['perception'].values() and dist(self.newinfo['posTerrain'], posResident) == 1: # si à coter de recepteur return action Donner
                            self.nextMove = ["DONNER", ""]
                            self.requete = None 
                            self.is_etatfinish = True
                        else: # sinon action Avancer se rapprocher du recepteur
                            self.actionMaker = MouvementDansMap(self, self.newinfo['posTerrain'], posResident, self.carte_mental)
                            self.nextMove = self.actionMaker.nextAction()
    
    def get_NeuMannVisionBYpos(self,x,y):
        """ Donne la vision N S E O de la grille à la pos @x,@y
        return {"N":N, "S":S, "E":E,"O":O} """
        hauteur,largeur = self.infoDeBase["tailleCarte"].values()
        if (x >= hauteur and x <= 0) or (y >= largeur and y <= 0):
            print("[ENVIRONMENT][get_perception][error] x or y out of range")
            return None
        N = self.carte_mental[x-1][y]
        S = self.carte_mental[x+1][y]
        E = self.carte_mental[x][y+1]
        O = self.carte_mental[x][y-1]
        return {"N":N, "S":S, "E":E, "O":O}

    def checkRequest(self):
        if self.requete is None:
            self.on = False
        else:
            r = self.environment.get_residentInfoByRID(self.requete['resident'])
            if r is None:
                self.errorMsg = "Le résident n'existe pas"
                self.requete = None
                return
            if r['id'] in self.innaccessiblePlace:
                self.errorMsg = "Le résident n'est pas accessible"
                self.requete = None



    def isPossibleToDelivery(self):
        if 'A' in self.innaccessiblePlace:
            self.errorMsg = "l'armoire n'est pas accessible"
            return False
        if 'D' in self.innaccessiblePlace:
            self.errorMsg = "le dictionnaire n'est pas accessible"
            return False
        return True
    
    def InnaccessiblePlace(self):
        L = []
        for elt,coo in [('A',self.infoDeBase["armoirePos"]),('D' ,self.infoDeBase["dictionnairePos"])] + [(r['id'],r["position"]) for r in self.infoDeBase["residents"] ]:
            x,y = coo
            if not self.is_accessible(x,y):
                L.append(elt)
        return L
    
    def is_accessible(self,x,y):
        return '.' in self.get_NeuMannVisionBYpos(x,y).values()


def dist(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])