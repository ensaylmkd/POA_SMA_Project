from parcours import *

class Arbre:
    def __init__(self, valeur,  pere=None):
        #Pour pouvoir construire le chemin
        self.valeur = valeur #(x,y)
        self.pere = pere

def abs(a) :
    if a < 0 : 
        return -a
    else : 
        return a

class Explorer:
    def __init__(self, taille_carte):
        self.pile = [   ]
        self.tab_marquage = []
        self.chemin = []
        #On initialise une carte de la bonne taille
        self.carte_mental =[["#" if x == 0 or y == 0 or x == taille_carte[0]-1 or y == taille_carte[1]-1 else "?" for y in range(taille_carte[0])]for x in range(taille_carte[0])]
        self.is_finish = False

    def functionExplorer(self, pos, newinfo) :
        """Lance l'exploration de la map, pour remplir la carte mentale"""
        pile = self.pile
        map = self.carte_mental
        tab_marquage = self.tab_marquage
        map[pos[0]][pos[1]] = "."          # ma case est forcément libre
        #pos = Agent.newinfo["posTerrain"]
        pos = tuple(pos)
        if pos not in tab_marquage :#si on a pas déjà visiter pos, on regarde les voisins
            tab_marquage.append(pos)
            v_g = (pos[0], pos[1]-1)
            v_d = (pos[0], pos[1]+1)
            v_h = (pos[0]-1, pos[1])
            v_b = (pos[0]+1, pos[1])
            #interroger environnement sur les voisins :
            vu = newinfo["perception"]
            if (v_g not in tab_marquage) and v_g not in pile:
                #interroger sur nature de v_g (murs etc)
                map[v_g[0]][v_g[1]] = vu["O"]
                if (map[v_g[0]][v_g[1]] == ".") and v_g not in tab_marquage and v_g not in pile:
                    pile.append(v_g)
            #on fait pareil pour les autres voisins
            if (v_d not in tab_marquage) and v_d not in pile:
                #interroger sur nature de v_d (murs etc)
                map[v_d[0]][v_d[1]] = vu["E"]
                if (map[v_d[0]][v_d[1]] == ".") and v_d not in tab_marquage and v_d not in pile:
                    pile.append(v_d)
            if (v_h not in tab_marquage) and v_h not in pile :
                #interroger sur nature de v_h
                map[v_h[0]][v_h[1]] = vu["N"]
                if (map[v_h[0]][v_h[1]] == ".") and v_h not in tab_marquage and v_h not in pile:
                    pile.append(v_h)
            if (v_b not in tab_marquage) and v_b not in pile:
                #interroger sur nature de v_b
                map[v_b[0]][v_b[1]] = vu["S"]
                if (map[v_b[0]][v_b[1]] == ".") and v_b not in tab_marquage and v_b not in pile:
                    pile.append(v_b)
        if self.chemin:
            nxt = self.chemin[0]
            if abs(nxt[0]-pos[0]) + abs(nxt[1]-pos[1]) != 1:
                self.chemin = []
        if not pile and not self.chemin:#si pile vide et route vide, alors on a fini
            self.is_finish = True
            return ["ATTENDRE", None]
        # on retire de la pile les cases déjà visitées
        pile[:] = [p for p in pile if p not in tab_marquage]

        # on cherche le plus court chemin parmi toutes les cibles possibles
        meilleur = []
        for cible in list(pile):
            chemin = deplacement(pos, cible, map)
            if not chemin:
                pile.remove(cible)          # case inatteignable : on l'oublie
            elif not meilleur or len(chemin) < len(meilleur):
                meilleur = chemin

        if not meilleur:                    # plus rien à explorer
            self.is_finish = True
            return ["ATTENDRE", None]

        return direction(pos, meilleur[1])# meilleur[0] est pos 
