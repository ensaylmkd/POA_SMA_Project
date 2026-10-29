#!/usr/bin/env python3
from collections import deque
from Environment import *
from src.agentExemple import *

class Arbre:
    def __init__(self, valeur,  pere=None):
        self.valeur = valeur #(x,y)
        self.pere = pere

def deplacement(pos_dep, pos_but, map) :
    """Pour aller d'une pos_initiale a une pos_but a l'aide d'un parcours en largeur qui calcule le chemin optimal a l'aide de la map (mentale du robot)"""
    pos_dep = tuple(pos_dep)
    pos_but = tuple(pos_but)
    if pos_dep == pos_but:
        return [pos_dep]
    f = deque()
    tab_marquage = []
    tab_marquage.append(pos_dep)
    racine = Arbre(pos_dep)
    f.append(racine)
    but = False
    while f and but == False:
        arb_cour = f.popleft()
        pos = arb_cour.valeur
        v_g = (pos[0], pos[1]-1)
        v_d = (pos[0], pos[1]+1)
        v_h = (pos[0]-1, pos[1])
        v_b = (pos[0]+1, pos[1])
        if (map[v_g[0]][v_g[1]] == "." and v_g not in tab_marquage):#si on peut se deplacer alors on ajoute a l'arbre et a la file 
            tab_marquage.append(v_g)
            abg = Arbre(v_g, arb_cour)
            f.append(abg)
            if (v_g == pos_but):
                        ab_but = abg
                        but = True
        if (map[v_d[0]][v_d[1]] == "." and v_d not in tab_marquage):
            tab_marquage.append(v_d)
            abd = Arbre(v_d, arb_cour)
            f.append(abd)
            if (v_d == pos_but):
                        ab_but = abd
                        but = True
        if (map[v_h[0]][v_h[1]] == "." and v_h not in tab_marquage):
            tab_marquage.append(v_h)
            abh = Arbre(v_h, arb_cour)
            f.append(abh)
            if (v_h == pos_but):
                        ab_but = abh
                        but = True
        if (map[v_b[0]][v_b[1]] == "." and v_b not in tab_marquage):
            tab_marquage.append(v_b)
            abb = Arbre(v_b, arb_cour)
            f.append(abb)
            if (v_b == pos_but):
                        ab_but = abb
                        but = True   
    #On trouve pas le chemin
    if but == False:
        return []
    #on trouve le chemin 
    p = ab_but
    chemin = []
    while p != None :
        chemin.append(p.valeur)
        p = p.pere
    chemin.reverse()#Le chemin est en sens inverse donc on utilise reverse pour avoir chemin[0] = pos_dep et chemin[n] = pos_but
    return chemin

def parcours_map(pos_dep, map, Agent, environment) :
    """Pour lancer le parcours de la map par l'agent afin de remplir une carte mentale"""
    tab_marquage = []
    pile = []
    pile.append(pos_dep)
    while pile != []:
        pos = pile.pop()
        if pos in tab_marquage :
            continue
        #Avancer agent sur case pos de coord (x, y)
        percep = environment.get_perception(Agent.IDAgent)
        chemin = deplacement(tuple(percep["posTerrain"]), pos, map)
        if chemin == []:#Il y a pas de chemin pour aller à pos
            continue
        mouvement(chemin, Agent)
        if pos not in tab_marquage :
            tab_marquage.append(pos)
            v_g = (pos[0], pos[1]-1)
            v_d = (pos[0], pos[1]+1)
            v_h = (pos[0]-1, pos[1])
            v_b = (pos[0]+1, pos[1])
            #interroger environnement sur les voisins :
            vu = environment.get_perception(Agent.IDAgent)["perception"]
            if (v_g not in tab_marquage) :
                #interroger sur nature de v_g (murs etc)
                map[v_g[0]][v_g[1]] = vu["O"]
                if (map[v_g[0]][v_g[1]] == "."):
                    pile.append(v_g)
            #on fait pareil pour les autres voisins
            if (v_d not in tab_marquage) :
                #interroger sur nature de v_d (murs etc)
                map[v_d[0]][v_d[1]] = vu["E"]
                if (map[v_d[0]][v_d[1]] == "."):
                    pile.append(v_d)
            if (v_h not in tab_marquage) :
                #interroger sur nature de v_h
                map[v_h[0]][v_h[1]] = vu["N"]
                if (map[v_h[0]][v_h[1]] == "."):
                    pile.append(v_h)
            if (v_b not in tab_marquage) :
                #interroger sur nature de v_b
                map[v_b[0]][v_b[1]] = vu["S"]
                if (map[v_b[0]][v_b[1]] == "."):
                    pile.append(v_b)
    return map

def mouvement(chemin, Agent) :
    """Pour faire bouger l'agent selon chemin"""
    environment = Agent.environment

    for i in range(1, len(chemin)):
        x1, y1 = chemin[i - 1]
        x2, y2 = chemin[i]
        if x2 == x1 - 1:
            Agent.nextMove = ["AVANCER", "HAUT"]
        elif x2 == x1 + 1:
            Agent.nextMove = ["AVANCER", "BAS"] 
        elif y2 == y1 - 1:
            Agent.nextMove = ["AVANCER", "GAUCHE"]
        elif y2 == y1 + 1:
            Agent.nextMove = ["AVANCER", "DROITE"]
        environment._handleAction(Agent.IDAgent, Agent.nextMove)