from src.agentExemple import *

class Environment:
    def __init__(self, carte, scenario, dictionnaire, armoire):
        self.carte = carte
        self.scenario = scenario
        self.dictionnaire = dictionnaire
        self.armoire = armoire

        self.grid = [list(ligne) for ligne in self.carte['grille']]

        self.agents = []
        self.agentsPos = []

        self._initAgent()

    def _initAgent(self):
        # for i in range(len(self.carte['depart_robot'])):
            # self.agents.append(AgentExemple(self,i))
            # self.agentsPos.append(self.carte['depart_robot'][i])
        self.agents.append(AgentExemple(self,0))
        self.agentsPos.append(self.carte['depart_robot'])


    # Ce que voit le robot au depart : sa position, celle de l'armoire, celle
    # du dictionnaire, et celles des residents. Les murs, eux, ne sont PAS
    # connus a priori, et le contenu des casiers non plus (enonce 3.2 et 3.3).
    # Ne lisez ni carte["grille"], ni le champ "objet" des casiers : votre
    # agent n'y a pas droit.
    
    # ================ Communication [Agent <=> Environment] =====================
    def get_initAgent_info(self):
        """ Exemple :
        departRobot   : [6, 1]
        armoire        : [6, 4]
        dictionnaire   : [7, 6]
        casier depart  : [1, 0] 
        """
        return {"departRobot": self.carte['depart_robot'], 
                "armoirePos": self.carte['armoire']['position'],
                "dictionnairePos": self.carte['dictionnaire']['position'],
                "departCasier": self.armoire['casier_depart']
                 }
        
    def get_perception(self,id):
        hauteur,largeur = self.carte["dimensions"].values()
        x,y = self.agentsPos[id]
        if (x >= hauteur and x > 0) or (y >= largeur and y > 0) :
            print("[ENVIRONMENT][get_perception][error] x or y out of range")
            return None
        N = self.grid[x-1][y]
        S = self.grid[x+1][y]
        E = self.grid[x][y+1]
        O = self.grid[x][y-1]
        return{ "N":N, 
                "S":S, 
                "E":E,
                "O":O }
    
    def get_agentsActions(self):
        return [a.nextMove for a in self.agents]

    #================ Action logique ================
    def moveAgent(self,idAgent,action):
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

        movement = _parseAction2Vec(action)
        x,y = self.agentsPos[idAgent]
        new_x, new_y = movement[0] + x , movement[1] + y 
        if self.grid[new_x][new_y] == ".":
            self.agentsPos[idAgent] = [new_x,new_y]
            
            self.grid[new_x][new_y] = self.grid[x][y]
            self.grid[x][y] = '.'
        else:
            print("[MoveAgent] BONK!! l'agent id", idAgent ," a taper dans quelque chose")

    def _handleAction(self,id,action):
        match action[0].upper():
            case "AVANCER":
                self.moveAgent(id,action[1])
            case "CONSULTER":
                pass
            case "CHERCHER":
                pass
            case "PRENDRE":
                pass
            case "DONNER":
                pass
            case "ATTENDRE":
                pass
            case _:
                print("[Env.HandleAction] Bah ça existe pas ", action[0], "mdr")

    def makeAgentNextMove(self):            
        actions = self.get_agentsActions()
        for i in range(len(actions)):
            self._handleAction(i,actions[i])
        print("[MakeAgentNextMove] ActionsAgents :", actions)

 #===================================================================

 #================ Main Script =====================
    def timeStep(self):
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


