#!/usr/bin/env python3
from collections import deque
from src.Environment import *
from src.Robot import *

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

def direction(pos1, pos2) :
    """Donne une direction au d�placement que sur des positions voisines"""
    x1 , y1 = pos1
    x2, y2 = pos2
    if x2 == x1 - 1:
        return ["AVANCER", "N"]
    elif x2 == x1 + 1:
        return ["AVANCER", "S"]
    elif y2 == y1 - 1:
        return ["AVANCER", "O"]
    elif y2 == y1 + 1:
        return ["AVANCER", "E"]

def mouvement(chemin) :
    """Pour cr�er une liste afin de bouger l'agent selon chemin"""
    list_action = []
    if chemin == [] :
        return None
    for i in range(1, len(chemin)):
        list_action.append(direction(chemin[i-1], chemin[i]))
    return list_action