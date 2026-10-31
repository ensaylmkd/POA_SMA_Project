#!/usr/bin/env python3

import sys
from pathlib import Path
import time
import tkinter as tk

import reconfort_io as rio

TAILLE_CASE_AFFICHAGE = 30
DELAI_AFFICHAGE = 50

# Couleurs de la carte
COULEURS = {
    '#': '#4a4a4a',   # mur
    ' ': '#f8f9fa',   # case inexplorée
    '.': '#cccccc',   # case exploré
    'R': '#e63946',   # robot
    'P': '#f4a261',   # personne
    'A': "#70574e",   # armoire
    'D': '#2a9d8f',   # dictionnaire
}

# Couleurs des cases perçues
COULEURS_FONCEES = {
    '#': '#2b2b2b',   # mur
    ' ': '#dcdfe4',   # case inexplorée
    '.': '#b0b0b0',   # sol exploré
    'R': '#c1121f',   # robot
    'P': '#d97706',   # personne
    'A': "#5e4138",   # armoire
    'D': '#1f7a6f',   # dictionnaire
}

# Couleurs de l'intensité des émotions dans l'armoire
COULEURS_INTENSITE = {
    0: "#3dc000",   # intensité 1 : vert clair
    1: "#e2751c",   # intensité 2 : orange
    2: "#c71212",   # intensité 3 : rouge
}

#######################################################
######################    MAP    ######################
#######################################################
def initMap(mapCharged):
    width=len(mapCharged[0])
    height=len(mapCharged)

    map = [['#' for _ in range(width)] for _ in range(height)]

    for r in range(1, height - 1):
        for c in range(1, width - 1):
            map[r][c] = ' '

    return map

def updateMap(position, perception, map):
    r, c = position

    perçues = []

    if map[r - 1][c] == ' ' or map[r - 1][c] == 'R':
        map[r - 1][c] = perception['N']
    perçues.append((r - 1, c))

    if map[r + 1][c] == ' ' or map[r + 1][c] == 'R':
        map[r + 1][c] = perception['S']
    perçues.append((r + 1, c))

    if map[r][c + 1] == ' ' or map[r][c + 1] == 'R':
        map[r][c + 1] = perception['E']
    perçues.append((r, c + 1))

    if map[r][c - 1] == ' ' or map[r][c - 1] == 'R':
        map[r][c - 1] = perception['O']
    perçues.append((r, c - 1))

    map[r][c] = 'R'

    return map, perçues

def drawMap(canvas, map, perçues, resident):
    canvas.delete("all")

    height = len(map)
    width = len(map[0])

    for r in range(height):
        for c in range(width):
            case = map[r][c]

            if (r, c) in perçues:
                couleur = COULEURS_FONCEES.get(case, '#bbbbbb')
            else:
                couleur = COULEURS.get(case, '#cccccc')

            x1 = c * TAILLE_CASE_AFFICHAGE
            y1 = r * TAILLE_CASE_AFFICHAGE
            x2 = x1 + TAILLE_CASE_AFFICHAGE
            y2 = y1 + TAILLE_CASE_AFFICHAGE

            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=couleur,
                outline="#888888"
            )

            if case == 'R':
                canvas.create_text(
                    (x1 + x2) // 2,
                    (y1 + y2) // 2,
                    text="R",
                    font=("Arial", 16, "bold"),
                    fill="#ffffff"
                )

            if case == 'P':
                for res in resident:
                    if res['position'] == [r, c]:
                        canvas.create_text(
                            (x1 + x2) // 2,
                            (y1 + y2) // 2,
                            text=res['id'],
                            font=("Arial", 12, "bold"),
                            fill="#ffffff"
                        )
                        break

#######################################################
######################  ARMOIRE  ######################
#######################################################
def initMapArmoire():
    nb_colonnes = 8
    nb_lignes = 3

    map_armoire = [['?' for _ in range(nb_colonnes)] for _ in range(nb_lignes)]

    return map_armoire


def updateMapArmoire(coord_casier, map_armoire, contenucasiers):
    intensite, emotion = coord_casier

    map_armoire[intensite][emotion] = contenucasiers

    return map_armoire

def prendreMapArmoire(coord_casier, map_armoire):
    intensite, emotion = coord_casier

    map_armoire[intensite][emotion] = ''
    
    return map_armoire


def drawMapArmoire(canvas, map_armoire, emotions, perçues):
    canvas.delete("all")

    height = 3         
    width = 8       

    TAILLE_BLOC = 3 * TAILLE_CASE_AFFICHAGE   

    largeur_armoire = width * TAILLE_BLOC
    hauteur_armoire = height * TAILLE_BLOC

    canvas.create_rectangle(
        0,
        25,
        largeur_armoire,
        hauteur_armoire + 25,
        fill=COULEURS['A'],
        outline=""
    )

    for r in range(height):
        for c in range(width):
            case = map_armoire[r][c]
            vue = [r,c] == perçues

            for sr in range(3):
                for sc in range(3):
                    x1 = c * TAILLE_BLOC + sc * TAILLE_CASE_AFFICHAGE
                    y1 = r * TAILLE_BLOC + sr * TAILLE_CASE_AFFICHAGE + 25
                    x2 = x1 + TAILLE_CASE_AFFICHAGE
                    y2 = y1 + TAILLE_CASE_AFFICHAGE

                    if sr < 2:
                        remplissage = COULEURS_INTENSITE[r]
                    elif vue:
                        remplissage = "#5d4037"  
                    else:
                        remplissage = ""

                    canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=remplissage,
                        outline="#888888"
                    )

            x_centre = c * TAILLE_BLOC + TAILLE_BLOC // 2
            y_centre = r * TAILLE_BLOC + TAILLE_BLOC // 2 + 25

            if vue:
                canvas.create_polygon(
                    x_centre - 15, y_centre + 40,
                    x_centre + 15, y_centre + 40,
                    x_centre, y_centre + 12,
                    fill="#ffd166",
                    outline="#3f2d20"
                )

            if case:
                texte = case if len(case) <= 8 else case[:7] + "…"
                canvas.create_text(
                    x_centre,
                    y_centre,
                    text=texte,
                    font=("Arial", 12, "bold"),
                    fill="#3f2d20"
                )

    for i in range(width + 1):
        x = i * TAILLE_BLOC

        if i == 0:
            x = 3

        canvas.create_line(
            x, 25,
            x, hauteur_armoire + 25,
            fill=COULEURS['A'],
            width=3
        )

    for i, emotion in enumerate(emotions):
        x_centre = i * TAILLE_BLOC + TAILLE_BLOC // 2

        canvas.create_text(
            x_centre,
            12,
            text=emotion,
            font=("Arial", 11, "bold"),
            fill="black"
        )


#######################################################
#####################   UTILS   #######################
#######################################################
def initDrawing(trace, map):
    height = len(map)
    width = len(map[0])

    height_armoire = 3 * 3
    width_armoire = 8 * 3

    root = tk.Tk()
    root.title("Visualisation du robot")

    header = tk.Frame(root)
    header.pack(fill="x")

    label_pas = tk.Label(
        header,
        text=f"Pas 0 / {len(trace['pas'])}",
        font=("Arial", 14, "bold")
    )
    label_pas.pack(side="left", padx=10, pady=5)

    label_liv = tk.Label(
        header,
        text=f"Livraison 0 / {trace['resume']['demandes']}",
        font=("Arial", 14, "bold")
    )
    label_liv.pack(side="right", padx=10, pady=5)

    zone = tk.Frame(root)
    zone.pack()

    canvas = tk.Canvas(
        zone,
        width=width * TAILLE_CASE_AFFICHAGE,
        height=height * TAILLE_CASE_AFFICHAGE,
        bg="white"
    )
    canvas.pack()

    canvas_armoire = tk.Canvas(
        zone,
        width=width_armoire * TAILLE_CASE_AFFICHAGE,
        height=height_armoire * TAILLE_CASE_AFFICHAGE + 25,
        bg="white"
    )
    canvas_armoire.pack_forget()

    hand = tk.Frame(root)
    hand.pack(fill="x")

    label_hand = tk.Label(
        hand,
        text="Main : vide",
        font=("Arial", 14, "bold")
    )
    label_hand.pack(side="left", padx=8, pady=8)

    root.update()

    return root, canvas, canvas_armoire, label_pas, label_liv, label_hand

#######################################################
######################   MAIN   #######################
#######################################################
def main(argv):
    if len(argv) != 2:
        print(__doc__.strip())
        return 2

    chemin_trace = Path(argv[1])

    try:
        trace = rio.charger_trace(chemin_trace)
        carte = rio.charger_carte("cartes/" + trace["carte"] + ".json")
        scenario = rio.charger_scenario("scenarios/" + trace["scenario"] + ".json")
        armoire = rio.charger_armoire("donnees/" + scenario["armoire"] + ".json")
    except rio.ErreurFichier as err:
        print(f"erreur de chargement : {err}", file=sys.stderr)
        return 1

    map = initMap(carte['grille'])
    map_armoire = initMapArmoire()
    resident = carte['residents']

    root, canvas, canvas_armoire, label_pas, label_liv, label_hand = initDrawing(trace, map)

    p=0
    l=0

    dans_armoire = False

    for step in trace["pas"]:
        p += 1
        label_pas.config(text=f"Pas {p} / {len(trace['pas'])}")
        label_liv.config(text=f"Livraison {l} / {trace['resume']['demandes']}")

        if "action" in step and step["action"] == "CHERCHER" and not dans_armoire:
            canvas.pack_forget()
            canvas_armoire.pack(side="left", padx=10, pady=10)
            dans_armoire = True
            drawMapArmoire(canvas_armoire, map_armoire, armoire['emotions'], step["casier"])
            root.update()
            root.after(DELAI_AFFICHAGE * 5)
            

        if "action" in step and step["action"] == "PRENDRE" and dans_armoire:
            map_armoire = updateMapArmoire(step['casier'], map_armoire, "")
            drawMapArmoire(canvas_armoire, map_armoire, armoire['emotions'], step["casier"])
            item = step["argument"].lower()

            label_hand.config(text=f"Main : {item}")

            root.update()
            root.after(DELAI_AFFICHAGE * 5)

            canvas_armoire.pack_forget()
            canvas.pack(side="left", padx=10, pady=10)
            dans_armoire = False

        
        elif "action" in step and step["action"] == "DONNER":
            label_hand.config(text=f"Main : vide")
        # Lucas : A decommenter si il y a livraison dans la trace
        #     if trace["livraison"][l]["success"]:
        #         l+=1
        else:
            if dans_armoire:
                map_armoire = updateMapArmoire(step['casier'], map_armoire, armoire['casiers'][step['casier'][0] * 8 + step['casier'][1]]['objet'])
                drawMapArmoire(canvas_armoire, map_armoire, armoire['emotions'], step["casier"])

                root.update()
                root.after(DELAI_AFFICHAGE * 5) 
            else:
                map, perçues = updateMap(step['position'], step['perception'], map)
                drawMap(canvas, map, perçues, resident)

        root.update()
        root.after(DELAI_AFFICHAGE)

    root.mainloop()

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))