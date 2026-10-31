from src.agentExemple import *
from consultDico import EmotionInfoFromSentence
from MouvementDansArmoire import getPossibleObjects

class Environment:
    # ================ Init =======================
    def __init__(self, carte, scenario, dictionnaire, armoire, trace):
        # constante DATA
        self.trace = trace
        self.carte = carte
        self.scenario = scenario
        self.dictionnaire = dictionnaire
        self.armoire = armoire
        
        # constante DATA et trace dynamique
        self.demandes = {}
        for elt in self.scenario["demandes"]:
            intensite, emotion = EmotionInfoFromSentence(elt["message"])
            L = getPossibleObjects(armoire, emotion,intensite)
            self.demandes[elt["numero"]] = {"demande": elt,
                                            "InfoDico": [intensite, emotion] ,
                                            "PossibleObjects": L,
                                            "casier_choisi": None,
                                            "repli": None,
                                            "objet": None,
                                            "pas_utilises": 1,
                                            "succes": False,
                                            "motif_echec": None}
        
        self.commentaire = ""

        # dynamique DATA environment
        self.grid = [list(ligne) for ligne in self.carte['grille']]
        
        self.casiers = [[None for _ in range(8)] for _ in range(3)]
        for elt in self.armoire["casiers"]:
            self.casiers[elt["ligne"]][elt["colonne"]] = {key: val for key, val in elt.items() if key not in ["ligne","colonne"]}
        
        self.agentsDemandesPile = self.scenario['demandes'].copy()

        # dynamique Data des agents
        self.agents = []
        self.agentsPosTerrain = []
        self.agentsPosCasier = []
        self.agentsInventory = []
        self.agentsDemandesData = []

        # création des agents
        self._initAgent()

    def _initAgent(self):
        # for i in range(len(self.carte['depart_robot'])):
            # self.agents.append(AgentExemple(self,i))
            # self.agentsPosTerrain.append(self.carte['depart_robot'][i])
            # self.agentsPosCasier.append(self.armoire["casier_depart"][i])
            # self.agentsInCasier.append(False)
            # self.agentsInventory.append(None)

        
        self.agentsPosTerrain.append(self.carte['depart_robot'])
        self.agentsPosCasier.append(self.armoire["casier_depart"])
        self.agentsInventory.append(None)
        self.agentsDemandesData.append([None,None])
        self.agents.append(AgentExemple(self,0))

    # ==========================================================================

    # =================== Trace ================================================
    def traceLivraisonAgent(self,IDAgent):
        data = self.get_demandeAllInfoFromIDAgent(IDAgent)
        data['repli'] = "aucun" # Lucas : ca plante sinon
        data['motif_echec'] = "oui"
        self.trace.ajouter_livraison(self.agentsDemandesData[IDAgent][0],
                                    data["demande"]["resident"],
                                    data["InfoDico"][1],
                                    data["InfoDico"][0],
                                    data["casier_choisi"],
                                    data["repli"],
                                    data["objet"],
                                    data["succes"],
                                    data["motif_echec"]
                                    )

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
        if (x > hauteur and x >= 0) or (y > largeur and y >= 0): # Lucas : cest ente 0 et 2 | 0 et 7
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
        if (x >= 3 and x > 0) or (y >= 8 and y > 0): # Lucas : cest ente 0 et 2 | 0 et 7
            print("[ENVIRONMENT][get_perception][error] x or y out of range")
            return None
        return self.casiers[x][y]
    
    def get_demandeAllInfoFromIDAgent(self,IDAgent):
        return self.demandes[self.agentsDemandesData[IDAgent][0]] if self.agentsDemandesData[IDAgent][0] is not None else None

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
            'InfoDemande': self.agentsDemandesData[IDAgent][1],
        }
    
    def get_NextDemande(self,IDAgent):
        if self.agentsDemandesData[IDAgent][0] is not None:
            self.traceLivraisonAgent(IDAgent)
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
                self.chercherAgent(IDAgent,action[1])
            case "PRENDRE":
                self.prendreAgent(IDAgent)
            case "DONNER":
                self.donnerAgent(IDAgent)
            case "ATTENDRE":
                pass
            case _:
                print("[Env.HandleAction] Bah ça existe pas ", action[0], "mdr")
        x,y = self.agentsPosCasier[IDAgent]
        self.trace.ajouter_pas(
            demande = self.agentsDemandesData[IDAgent][0],
            position = self.agentsPosTerrain[IDAgent],
            casier = self.agentsPosCasier[IDAgent],
            action = action[0].upper(),
            argument = action[1].upper(),
            perception = self.get_NeuMannVisionBYidAgent(IDAgent),
            contenu_casier = self.get_item(x,y),
            commentaire = self.commentaire
            )

    #/////////////// All Action Handler /////////////////
    def _parseAction2Vec(self,action):
            res = (0,0)
            match action.upper():
                case "N":
                    res = (-1,0)
                case "S":
                    res = (1,0)
                case "O":
                    res = (0,-1)
                case "E":
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
            self.commentaire = "l'agent se déplace"
        else:
            print("[MoveAgent.grid_MoveAgent] BONK!! l'agent id", IDAgent ," a taper dans quelque chose :: ",self.grid[new_x][new_y])
            self.commentaire = "BONK!! l'agent a taper dans quelque chose, il commence a pleurer (gros bb)"
        
    def moveAgent(self,IDAgent,action):
        """Action Avancer"""
        vector = self._parseAction2Vec(action)
        self._grid_moveAgent(IDAgent,vector)
        print("[avancerAgent]Succes: l'agent ",IDAgent,"se déplace")
        
            
    # Pour CONSULTER
    def consulteAgent(self,IDAgent):
        """Action Consulter"""
        if self.agentsDemandesData[IDAgent] is None:
            print("[ConsulterAgent][error]l'agent",IDAgent," n'a pas de demande en cours, faire nextDemande")
            self.commentaire = "L'agent n'a pas de demande en cours, il ne peut pas Consulter."
        elif 'D' not in self.get_NeuMannVisionBYidAgent(IDAgent).values():
            print("[ConsulterAgent][error]Le dictionnaire n'est pas à porter de l'agent",IDAgent)
            self.commentaire = "Le dictionnaire n'est pas à porter de l'agent, il ne peut pas le lire."
    
        elif self.agentsDemandesData[IDAgent][1] is not None:
            print("[ConsulterAgent][error]l'agent",IDAgent,"connait déja l'émotion de sa phrase ")
            self.commentaire = "L'agent connait déja l'émotion de sa phrase,il n'a pas besoin de Consulter."
            
        else:
            data = self.get_demandeAllInfoFromIDAgent(IDAgent)
            self.agentsDemandesData[IDAgent][1] = data['InfoDico']
            print("[ConsulterAgent]L'agent ", IDAgent, " a lu dans le dictionnaire",IDAgent)
            self.commentaire = "L'agent lit le dictionnaire, il sait maintenant l'émotion du résident."
    
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
            self.commentaire = "L'agent n'est pas à porter de l'Armoire, il ne peut pas chercher dedans."
            return
        
        combonus =""
        if self.agentsInventory[IDAgent] is not None:
            _putItem(IDAgent)
            print("[ChercherAgent] l'agent ",IDAgent,"a un item sur lui, il le pose avant de bouger son curseur")
            combonus = "L'agent avez un item, il le pose avant de chercher. "
        vector = self._parseAction2Vec(action)
        self._casier_moveAgent(IDAgent,vector)
        print("[ChercherAgent]Succes: l'agent ",IDAgent,"se déplace dans la vue armoire")
        self.commentaire = combonus + "L'agent se déplace dans la vue armoire"
   
    # Pour PRENDRE
    def prendreAgent(self,IDAgent):
        def _takeItem(IDAgent):
            x,y = self.agentsPosCasier[IDAgent]
            item = self.casiers[x][y].copy()
            self.casiers[x][y]['objet'] = None
            return item

        if 'A' not in self.get_NeuMannVisionBYidAgent(IDAgent).values():
            print("[PrendreAgent]ERROR: L'agent",IDAgent," n'est à porter de l'armoire")
            self.commentaire = "L'agent n'est pas à porter de l'Armoire, il ne peut pas chercher dedans."
        elif self.agentsInventory[IDAgent] is not None:
            print("[PrendreAgent] l'agent ",IDAgent,"a déja pris l'item de cette position (bouger le curseur pour le poser)")
            self.commentaire = "L'agent a déja pris l'item de cette position. Il ne peut pas le reprendre."

        else:
            item = _takeItem(IDAgent)
            self.agentsInventory[IDAgent] = item
            if item["objet"] :
                print("[prendreAgent]Succes: l'agent ",IDAgent,"prend l'objet",item)
                self.commentaire = "L'agent prend l'item."

            else:
                print("[PrendreAgent]Succes: l'agent ",IDAgent,"n'a rien pris")
                self.commentaire = "L'agent ne prend rien."
    
    # Pour DONNER
    def donnerAgent(self,IDAgent):
        def is_valideItem(IDAgent,item):
            data = self.get_demandeAllInfoFromIDAgent(IDAgent)
            return item['objet'] in data["PossibleObjects"].keys() # Lucas : mdr tu avais mis que item alors que item cest {'emotion': 'tristesse', 'intensite': 'moyenne', 'objet': 'couverture'}
        
        def updateData(IDAgent,item):
            data = self.get_demandeAllInfoFromIDAgent(IDAgent)
            i = self.agentsDemandesData[IDAgent][0]

            self.demandes[i]["casier_choisi"] = self.agentsPosCasier[IDAgent]
            self.demandes[i]["objet"] = item["objet"]
            self.demandes[i]["pas_utilises"] = 0
            if is_valideItem(IDAgent,item):
                self.demandes[i]["repli"] = data["PossibleObjects"][item["objet"]]
                self.demandes[i]["succes"] = True
                self.commentaire = "L'agent a livré l'objet. Le résident est satisfait"
            else:
                #self.demandes[i]["motif_echec"] = self.agents.errorMsg if self.agents.errorMsg is not None else "l'agent s'est trompé d'objet" # Lucas : ca marche pas errorMsg
                self.commentaire = "L'agent a livré l'objet. Le résident commence a pleuré (pas le bon objet)."
            
        target = self.get_demandeAllInfoFromIDAgent(IDAgent)["demande"]["resident"]
        ## Lucas : GROS PROBLEME YASSINE (en vrai pas autant juste target cest R1 ... mais dans la perception cest P pour tous les residents, moi j'ai fait un check dans case livraison de l'agent)
        # if target not in self.get_NeuMannVisionBYidAgent(IDAgent).values():  (ta ligne)
        if 'P' not in self.get_NeuMannVisionBYidAgent(IDAgent).values(): 
            print("[DonnerAgent]ERROR: L'agent",IDAgent," n'est à porter du resident",target)
            self.commentaire = "L'agent n'est pas à porter du résident à qui il doit livrer.("+target+")"
        elif self.agentsInventory[IDAgent] is None:
            print("[DonnerAgent]ERROR: L'agent",IDAgent," n'a pas d'objet sur lui")
            self.commentaire = "L'agent n'a pas d'objet sur lui, il ne peut pas Donner d'objet."
        else:
            item = self.agentsInventory[IDAgent]
            self.agentsInventory[IDAgent] = None
            
            updateData(IDAgent,item)

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
