from src.agentExemple import *
from consultDico import EmotionInfoFromSentence
from MouvementDansArmoire import getPossibleObjects

class Environment:
    # ================ Init =======================
    def __init__(self, carte, scenario, dictionnaire, armoire):
        # constante
        self.carte = carte
        self.scenario = scenario
        self.dictionnaire = dictionnaire
        self.armoire = armoire

        self.demandes = {}
        for elt in self.scenario["demandes"]:
            intensite, emotion = EmotionInfoFromSentence(elt["message"])
            L = getPossibleObjects(armoire, emotion,intensite)

            self.demandes[elt["numero"]] = {"demande": elt,
                                            "InfoDico": [intensite, emotion] ,
                                            "PossibleObjects": L,
                                            "repli": "aucun",
                                            "objet": None,
                                            "pas_utilises": 1,
                                            "succes": False,
                                            "motif_echec": None}

        # dynamique
        self.grid = [list(ligne) for ligne in self.carte['grille']]
        self.casiers = [[None for _ in range(8)] for _ in range(3)]
        for elt in self.armoire["casiers"]:
            self.casiers[elt["ligne"]][elt["colonne"]] = {key: val for key, val in elt.items() if key not in ["ligne","colonne"]}
        
        self.agentsDemandesPile = self.scenario['demandes'].copy()

        self.agents = []
        self.agentsPosTerrain = []
        self.agentsPosCasier = []
        self.agentsInventory = []
        self.agentsDemandesData = []

        self._initAgent()

    def _initAgent(self):
        # for i in range(len(self.carte['depart_robot'])):
            # self.agents.append(AgentExemple(self,i))
            # self.agentsPosTerrain.append(self.carte['depart_robot'][i])
            # self.agentsPosCasier.append(self.armoire["casier_depart"][i])
            # self.agentsInCasier.append(False)
            # self.agentsInventory.append(None)

        self.agents.append(AgentExemple(self,0))
        self.agentsPosTerrain.append(self.carte['depart_robot'])
        self.agentsPosCasier.append(self.armoire["casier_depart"])
        self.agentsInventory.append(None)
        self.agentsDemandesData.append(None)

    # ==========================================================================

    # Ce que voit le robot au depart : sa position, celle de l'armoire, celle
    # du dictionnaire, et celles des residents. Les murs, eux, ne sont PAS
    # connus a priori, et le contenu des casiers non plus (enonce 3.2 et 3.3).
    # Ne lisez ni carte["grille"], ni le champ "objet" des casiers : votre
    # agent n'y a pas droit.

    # ========================= Accesseur Utile ======================
    def get_NeuMannVisionBYpos(self,x,y):
        """ Donne la vision N S E O de la grille à la pos @x,@y
        return {"N":N, "S":S, "E":E,"O":O} """
        hauteur,largeur = self.carte["dimensions"].values()
        if (x >= hauteur and x > 0) or (y >= largeur and y > 0) :
            print("[ENVIRONMENT][get_perception][error] x or y out of range")
            return None
        N = self.grid[x-1][y]
        S = self.grid[x+1][y]
        E = self.grid[x][y+1]
        O = self.grid[x][y-1]
        return {"N":N, "S":S, "E":E, "O":O}
    
    def get_NeuMannVisionBYidAgent(self,IDAgent):
        """ Donne la vision N S E O de la grille à la pos de l'agent @IDAgent
        return {"N":N, "S":S, "E":E,"O":O} """
        x,y= self.agentsPosTerrain[IDAgent]
        return self.get_NeuMannVisionBYpos(x,y)

    def get_item(self,x,y):
        """renvoie l'objet de l'armoire en position @x,@y"""
        if (x >= 3 and x > 0) or (y >= 8 and y > 0) :
            print("[ENVIRONMENT][get_perception][error] x or y out of range")
            return None
        return self.casiers[x][y]
    
    def get_demandeAllInfoFromIDAgent(self,IDAgent):
        return self.demandes[self.agentsDemandesData[IDAgent]]

    # ================ Communication [Agent <== Environment] =====================
    def get_initAgent_info(self):
        """ Exemple :
        departRobot   : [6, 1]
        armoire        : [6, 4]
        dictionnaire   : [7, 6]
        casier depart  : [1, 0]
        residents : [{'id': 'R1', 'nom': 'Camille', 'position': [6, 11]}, {'id': 'R2', 'nom': 'Hugo', 'position': [3, 3]}]
        """
        return {"departRobot": self.carte['depart_robot'], 
                "armoirePos": self.carte['armoire']['position'],
                "dictionnairePos": self.carte['dictionnaire']['position'],
                "departCasier": self.armoire['casier_depart'],
                "residents": self.carte["residents"],
                "tailleCarte": self.carte["dimensions"]
                 }
    
    def get_perception(self,IDAgent):
        """return la perception Global de l'agent numero id
        exemple:
        {'perception': {'N': '.', 'S': '.', 'E': '.', 'O': '#'}, 
        'contenu_casier': {'emotion': 'joie', 'intensite': 'moyenne', 'objet': 'photo de famille'}, 
        'posTerrain': [6, 1], 
        'posCasier': [1, 0]}
        """
        x2,y2 = self.agentsPosCasier[IDAgent]
        return {
            'perception':self.get_NeuMannVisionBYidAgent(IDAgent),
            'contenu_casier': self.get_item(x2,y2),
            'posTerrain': self.agentsPosTerrain[IDAgent],
            'posCasier': self.agentsPosCasier[IDAgent],
            'InfoDemande': self.agentsInfoData[IDAgent][1],
        }
    
    def get_NextDemande(self,IDAgent):
        if len(self.agentsDemandesPile) > 0:
            demande = self.agentsDemandesPile.pop(0)
            self.agentsDemandesData[IDAgent] = [demande['numero'] , None ]
            return demande
        else:
            return None 

    # ================ Communication [Agent ==> Environment] =====================

    def get_agentsActions(self):
        return [a.nextMove for a in self.agents]

    # ======================================== Action logique ============================================

    # ///////////// MAIN Action Logique function ////////////
    def _handleAction(self,IDAgent,action):
        match action[0].upper():
            case "AVANCER":
                self.moveAgent(IDAgent,action[1])
            case "CONSULTER":
                self.consulteAgent(IDAgent)
            case "CHERCHER":
                self.chercherAgent(IDAgent)
            case "PRENDRE":
                self.prendreAgent(IDAgent)
            case "DONNER":
                pass
            case "ATTENDRE":
                pass
            case _:
                print("[Env.HandleAction] Bah ça existe pas ", action[0], "mdr")

    #/////////////// All Action Handler /////////////////
    def _parseAction2Vec(action):
            res = (0,0)
            match action.upper():
                case "HAUT":
                    res = (-1,0)
                case "BAS":
                    res = (1,0)
                case "GAUCHE":
                    res = (0,-1)
                case "DROITE":
                    res = (0,1)
                case "RIEN":
                    pass
                case _:
                    print("[moveAgent_Parser]",action," n'est pas une action possible")
            return res
    
    # Pour AVANCER 
    def _grid_moveAgent(self,IDAgent,vector):
        x,y = self.agentsPosTerrain[IDAgent]
        new_x, new_y = vector[0] + x , vector[1] + y 
        if self.grid[new_x][new_y] == ".":
            self.agentsPosTerrain[IDAgent] = [new_x,new_y]
            
            self.grid[new_x][new_y] = self.grid[x][y]
            self.grid[x][y] = '.'
        else:
            print("[MoveAgent.grid_MoveAgent] BONK!! l'agent id", IDAgent ," a taper dans quelque chose :: ",self.grid[new_x][new_y])
        
    def moveAgent(self,IDAgent,action):
        """Action Avancer"""
        vector = _parseAction2Vec(action)
        self._grid_moveAgent(IDAgent,vector)
        print("[avancerAgent]Succes: l'agent ",IDAgent,"se déplace")
            
    # Pour CONSULTER
    def consulteAgent(self,IDAgent):
        """Action Consulter"""
        if elf.agentsDemandesData[IDAgent] is None:
            print("[ConsulterAgent][error]l'agent",IDAgent," n'a pas de demande en cours, faire nextDemande")
        elif 'D' not in self.get_NeuMannVisionBYidAgent(IDAgent).values():
            print("[ConsulterAgent][error]Le dictionnaire n'est pas à porter de l'agent",IDAgent)
        elif self.agentsDemandesData[IDAgent][1] is not None:
            print("[ConsulterAgent][error]l'agent",IDAgent,"connait déja l'émotion de sa phrase ")
        else:
            data = get_demandeAllInfoFromIDAgent(IDAgent)
            self.agentsDemandesData[IDAgent][1] = data['InfoDico']
            print("[ConsulterAgent]L'agent ", IDAgent, " a lu dans le dictionnaire",IDAgent)
    
    # Pour CHERCHER
    def _casier_moveAgent(self,IDAgent,vector):
        x,y = self.agentsPosCasier[IDAgent]
        new_x, new_y = (vector[0] + x) % 3, (vector[1] + y) % 8
        self.agentsPosCasier[IDAgent] = [new_x,new_y]
    
    def chercherAgent(self,IDAgent,action):
        """Action Chercher"""
        def _putItem(IDAgent):
            x,y = self.agentsPosCasier[IDAgent]
            self.casiers[x][y] = self.agentsInventory[IDAgent]
            self.agentsInventory[IDAgent] = None

        if 'A' not in self.get_NeuMannVisionBYidAgent(IDAgent).values():
            print("[ChercherAgent]ERROR: L'armoire n'est pas à porter de l'agent",IDAgent)
            return

        if self.agentsInventory[IDAgent] is not None:
            _putItem(IDAgent)
            print("[ChercherAgent] l'agent ",IDAgent,"a un item sur lui, il le pose avant de bouger son curseur")
        vector = _parseAction2Vec(action)
        self._casier_moveAgent(IDAgent,vector)
        print("[ChercherAgent]Succes: l'agent ",IDAgent,"se déplace dans la vue armoire")
    
    # Pour PRENDRE
    def prendreAgent(self,IDAgent):
        def _takeItem(IDAgent):
            x,y = self.agentsPosCasier[IDAgent]
            item = self.casiers[x][y].copy()
            self.casiers[x][y]['objet'] = None
            return item

        if 'A' not in self.get_NeuMannVisionBYidAgent(IDAgent).values():
            print("[PrendreAgent]ERROR: L'agent",IDAgent," n'est à porter de l'armoire")
        elif self.agentsInventory[IDAgent] is not None:
            print("[PrendreAgent] l'agent ",IDAgent,"a déja pris l'item de cette position (bouger le curseur pour le poser)")
        else:
            item = _takeItem(IDAgent)
            self.agentsInventory[IDAgent] = item
            if item["objet"] :
                print("[prendreAgent]Succes: l'agent ",IDAgent,"prend l'objet",item)
            else:
                print("[PrendreAgent]Succes: l'agent ",IDAgent,"n'a rien pris")
    
    # Pour DONNER
    def donnerAgent(self,IDAgent):
        target = get_demandeAllInfoFromIDAgent(IDAgent)["demande"]["resident"]
        if target not in self.get_NeuMannVisionBYidAgent(IDAgent).values():
            print("[DonnerAgent]ERROR: L'agent",IDAgent," n'est à porter du resident",target)
        elif self.agentsInventory[IDAgent] is None:
            print("[DonnerAgent]ERROR: L'agent",IDAgent," n'a pas d'objet sur lui")
        else:
            item = self.agentsInventory[IDAgent]
            self.agentsInventory[IDAgent] = None

            #TODO vérifier si item correcte et ecrire trace 

 # ===================================================================

 # ================ Main Script =====================
    def makeAgentNextMove(self):            
        actions = self.get_agentsActions()
        for i in range(len(actions)):
            self._handleAction(i,actions[i])
        print("[MakeAgentNextMove] ActionsAgents :", actions)
 
    def timeStep(self):
        """ Avance de 1 temp en : 
        (1)updateState() les agents se mettent à jour sur l'environment 
        (2)compute_NextMove() préparent leur actions puis 
        (3)makeAgentNextMove() l'environment effectue l'action des agents   """
        # compute action by update new info 
        for a in self.agents:
            a.updateState()
            a.compute_NextMove()

        self.makeAgentNextMove()

# ==================================================

    def __str__(self):
        """ Affiche toute les info de l'environment.
        C'est pas si beau mais c'est bine pour debug si besoin """

        print("============== Carte :================")
        for key in self.carte.keys():
            print(f"\t{key}: ",self.carte[key])
        print("============== Scénario: ==============")
        for key in self.scenario.keys():
            print(f"\t{key}: ",self.scenario[key])
        print("======= Dictionnaire :============")
        for key in self.dictionnaire.keys():
            print(f"\t{key}: ",self.dictionnaire[key])
        print("======= Armoire :============")
        for key in self.armoire.keys():
            print(f"\t{key}: ",self.armoire[key])
        return ""
