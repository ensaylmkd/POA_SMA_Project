from src.parcours import *

class MouvementDansMap:
    def __init__(self, agent, posDepart, posObjectif, carte):
        self.agent = agent
        self.posDepart = tuple(posDepart)
        self.posObjectif = tuple(posObjectif)
        self.carte = carte

        cheminDeplacement = bestPathAmongNeighbor(posDepart, posObjectif, carte)
        self.listeDeplacement = mouvement(cheminDeplacement)

    def updateState(self):
        pass

    def nextAction(self): 
        if self.listeDeplacement != []:
            return self.listeDeplacement.pop(0)
        return ["ATTENDRE", ""]

def bestPathAmongNeighbor(posDepart, posObjectif, carte):
    l, c = posObjectif
    voisins = [
        (l - 1, c),  # N
        (l + 1, c),  # S
        (l, c - 1),  # O
        (l, c + 1),  # E
    ]

    chemins = []
    for v in voisins:
        if carte[v[0]][v[1]] == '.':
            chemins.append(deplacement(posDepart, v, carte))
    chemins = sorted(chemins, key=len)

    return chemins[0]