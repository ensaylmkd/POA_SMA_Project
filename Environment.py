from src.agentExemple import *

class Environment:
    # ================ Init =======================
    def __init__(self, carte, scenario, dictionnaire, armoire):
        self.carte = carte
        self.scenario = scenario
        self.dictionnaire = dictionnaire
        self.armoire = armoire

        self.grid = [list(ligne) for ligne in self.carte['grille']]

        self.casiers = [[None for _ in range(8)] for _ in range(3)]
        for elt in self.armoire["casiers"]:
            self.casiers[elt["ligne"]][elt["colonne"]] = {key: val for key, val in elt.items() if key not in ["ligne","colonne"]}

        self.agents = []
        self.agentsPosTerrain = []
        self.agentsPosCasier = []
        self.agentsInCasier = []
        self.agentsInventory = []

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
        self.agentsInCasier.append(False)
        self.agentsInventory.append(None)

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
                "residents": self.carte["residents"]
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
        }
    
    # ================ Communication [Agent ==> Environment] =====================

    def get_agentsActions(self):
        return [a.nextMove for a in self.agents]

    # ======================================== Action logique ============================================

    # ///////////// Main Action Logique function ////////////
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
    # Pour AVANCER 
    def _casier_moveAgent(self,IDAgent,vector):
        x,y = self.agentsPosCasier[IDAgent]
        new_x, new_y = (vector[0] + x) % 8 , (vector[1] + y) % 3
        self.agentsPosCasier[IDAgent] = [new_x,new_y]
    
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

        vector = _parseAction2Vec(action)
        if self.agentsInCasier[IDAgent]:
            self._casier_moveAgent(IDAgent)
        else:
            self._grid_moveAgent(IDAgent,vector)
            
    # Pour CONSULTER
    def consulteAgent(self,IDAgent):
        """Action Consulter"""
        if 'D' in self.get_NeuMannVisionBYidAgent(IDAgent).values():
            #TODO faire la logique de consulter (traitement de texte et tt)
            return
        else:
            print("[ConsulterAgent]Le dictionnaire n'est pas à porter de l'agent",IDAgent)
            return None
    
    # Pour CHERCHER
    def chercherAgent(self,IDAgent):
        """Action Chercher"""
        def _putItem(IDAgent):
            x,y = self.agentsPosCasier[IDAgent]
            self.casiers[x][y] = self.agentsInventory[IDAgent]
            self.agentsInventory[IDAgent] = None

        if 'A' in self.get_NeuMannVisionBYidAgent(IDAgent).values() and not self.agentsInCasier[IDAgent]:
            if self.agentsInventory[IDAgent]:
                _putItem(IDAgent)
                print("[ChercherAgent] l'agent ",IDAgent,"a déja un item sur lui, il le pose")
            self.agentsInCasier[IDAgent] = True
            print("[ChercherAgent]Succes: l'agent ",IDAgent,"rentre dans la vue armoire")
        
        else: # traitement error
            if not self.agentsInCasier[IDAgent]:
                print("[ChercherAgent]ERROR: L'armoire n'est pas à porter de l'agent",IDAgent)
            else:
                print("[ChercherAgent]ERROR: L'agent",IDAgent,"est déja dans l'armoire, il faut sois PRENDRE sois AVANCER")
    
    # Pour PRENDRE
    def prendreAgent(self,IDAgent):
        def _takeItem(IDAgent):
            x,y = self.agentsPosCasier[IDAgent]
            item = self.casiers[x][y].copy()
            self.casiers[x][y]['objet'] = None
            return item

        if 'A' in self.get_NeuMannVisionBYidAgent(IDAgent).values() and self.agentsInCasier[IDAgent]:
            item = _takeItem(IDAgent)
            self.agentsInCasier[IDAgent] = False
            if item["objet"] :
                print("[ChercherAgent]Succes: l'agent ",IDAgent,"prend l'objet",item)
            else:
                print("[ChercherAgent]ERROR: l'agent ",IDAgent,"n'a rien pris")
        else: # traitement error
            if not self.agentsInCasier[IDAgent]:
                print("[ChercherAgent]ERROR: L'agent",IDAgent," n'est pas dans la vue armoire")
            else:
                print("[ChercherAgent]ERROR: L'agent",IDAgent,"est déja dans l'armoire, il faut sois PRENDRE sois AVANCER")
    

 #===================================================================

 #================ Main Script =====================
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

#==================================================


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


