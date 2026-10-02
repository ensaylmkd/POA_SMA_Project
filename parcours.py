#!/usr/bin/env python3

import sys
from pathlib import P
from collections import deque
import reconfort_io as rio

class Arbre:
    def __init__(self, valeur,  pere=None):
        self.valeur = valeur
        self.pere = pere


def deplacement(pos_dep, pos_but, map) :
    """Pour aller d'une pos_initiale a une pos_but a l'aide d'un parcours en largeur qui calcule le chemin optimal a l'aide de la map (mentale du robot)"""
    f = deque()
    tab_marquage = []
    f.append(pos_dep)
    tab_marquage.append(pos_dep)
    racine = Arbre(pos_dep)
    but = False
    while f and but == False:
        pos = f.popleft()
        v_g = (pos[0], pos[1]-1)
        v_d = (pos[0], pos[1]+1)
        v_h = (pos[0]-1, pos[1])
        v_b = (pos[0]+1, pos[1])
        if (map[v_g[0]][v_g[1]] == "."):#si on peut se deplacer alors on ajoute a l'arbre et a la file 
            abg = Arbre(v_g, pos)
            f.append(abg)
        if (map[v_d[0]][v_d[1]] == "."):
            abd = Arbre(v_d, pos)
            f.append(abd)
        if (map[v_h[0]][v_h[1]] == "."):
            abh = Arbre(v_h, pos)
            f.append(abh)
        if (map[v_b[0]][v_b[1]] == "."):
            abb = Arbre(v_b, pos)
            f.append(abb)
        if (v_g == pos_but):
            ab_but = abg
            but = True
        if (v_d == pos_but):
            ab_but = abd
            but = True
        if (v_h == pos_but):
            ab_but = abh
            but = True  
        if (v_b == pos_but):
            ab_but = abb
            but = True
    #On trouve le chemin
    p = ab_but.pere
    chemin = []
    chemin.append(ab_but.valeur)
    while p.valeur != None :
        chemin.append(p.valeur)
        p = p.pere
    return chemin

def parcours_map(pos_dep, map, pile) :
    """Pour lancer le parcours de la map par l'agent afin de remplir une carte mentale"""
    tab_marquage = []
    pile.append(pos_dep)
    while pile != []:
        pos = pile.pop()
        #Avancer agent sur case pos de coord (x, y)
        if pos not in tab_marquage :
            tab_marquage.append(pos)
            v_g = (pos[0], pos[1]-1)
            v_d = (pos[0], pos[1]+1)
            v_h = (pos[0]-1, pos[1])
            v_b = (pos[0]+1, pos[1])
            #interroger environnement sur les voisins :
            if (v_g not in tab_marquage) :
                #interroger sur nature de v_g (murs etc)
                map[v_g[0]][v_g[1]] = "."#ou le retour genre '#' si mur, 'D' si dico etc
                if (map[v_g[0]][v_g[1]] == "."):
                    pile.append(v_g)
            #on fait pareil pour les autres voisins
            if (v_d not in tab_marquage) :
                #interroger sur nature de v_g (murs etc)
                map[v_d[0]][v_d[1]] = "."
                if (map[v_d[0]][v_d[1]] == "."):
                    pile.append(v_d)
            if (v_h not in tab_marquage) :
                #interroger sur nature de v_h
                map[v_h[0]][v_h[1]] = "."
                if (map[v_h[0]][v_h[1]] == "."):
                    pile.append(v_h)
            if (v_b not in tab_marquage) :
                #interroger sur nature de v_b
                map[v_b[0]][v_b[1]] = "."
                if (map[v_b[0]][v_b[1]] == "."):
                    pile.append(v_b)
    return map


def main(argv):
    if len(argv) != 5:
        print(__doc__.strip())
        return 2

    chemin_carte, chemin_scenario = Path(argv[1]), Path(argv[2])
    dossier_donnees, chemin_sortie = Path(argv[3]), Path(argv[4])

    try:
        carte = rio.charger_carte(chemin_carte)
        scenario = rio.charger_scenario(chemin_scenario)
        dictionnaire = rio.charger_dictionnaire(
            dossier_donnees / "dictionnaire.json")
        armoire = rio.charger_armoire(
            dossier_donnees / f"{scenario['armoire']}.json")
    except rio.ErreurFichier as err:
        print(f"erreur de chargement : {err}", file=sys.stderr)
        return 1

    print(f"carte        : {carte['nom']} "
          f"{carte['dimensions']['hauteur']}x{carte['dimensions']['largeur']}, "
          f"{len(carte['residents'])} residents")
    print(f"scenario     : {scenario['nom']}, "
          f"{len(scenario['demandes'])} demandes")
    print(f"dictionnaire : {len(dictionnaire['entrees'])} entrees")
    print(f"armoire      : {armoire['nom']}, "
          f"{len(armoire['casiers'])} casiers")
    print()

    # Ce que voit le robot au depart : sa position, celle de l'armoire, celle
    # du dictionnaire, et celles des residents. Les murs, eux, ne sont PAS
    # connus a priori, et le contenu des casiers non plus (enonce 3.2 et 3.3).
    # Ne lisez ni carte["grille"], ni le champ "objet" des casiers : votre
    # agent n'y a pas droit.
    print(f"depart robot   : {carte['depart_robot']}")
    print(f"armoire        : {carte['armoire']['position']}")
    print(f"dictionnaire   : {carte['dictionnaire']['position']}")
    print(f"casier depart  : {armoire['casier_depart']}")

    trace = rio.Trace(
        nom_carte=carte["nom"],
        nom_scenario=scenario["nom"],
        equipe=["A completer", "A completer"],
    )

    for demande in scenario["demandes"]:
        numero = demande["numero"]
        print(f"\ndemande {numero} ({demande['resident']}) : "
              f"{demande['message']}")
        print(f"  mots normalises : {rio.normaliser(demande['message'])}")

        trace.ajouter_pas(
            demande=numero,
            position=carte["depart_robot"],
            casier=armoire["casier_depart"],
            action="ATTENDRE",
            commentaire="robot de demonstration : ne fait rien",
        )
        trace.ajouter_livraison(
            demande=numero,
            resident=demande["resident"],
            emotion=None,
            intensite=None,
            casier_choisi=None,
            repli="aucun",
            objet=None,
            succes=False,
            motif_echec="agent non implemente",
        )

    trace.ecrire(chemin_sortie)
    print(f"\ntrace ecrite : {chemin_sortie}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
