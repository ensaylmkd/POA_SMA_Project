#!/usr/bin/env python3

import sys
from copy import deepcopy
from pathlib import Path
import tkinter as tk

import reconfort_io as rio


TAILLE_CASE_AFFICHAGE = 30
DELAI_AFFICHAGE = 50


COULEURS = {
    "#": "#4a4a4a",
    " ": "#f8f9fa",
    ".": "#cccccc",
    "R": "#e63946",
    "P": "#f4a261",
    "A": "#70574e",
    "D": "#2a9d8f",
}

COULEURS_FONCEES = {
    "#": "#2b2b2b",
    " ": "#dcdfe4",
    ".": "#b0b0b0",
    "R": "#c1121f",
    "P": "#d97706",
    "A": "#5e4138",
    "D": "#1f7a6f",
}

COULEURS_INTENSITE = {
    0: "#3dc000",
    1: "#e2751c",
    2: "#c71212",
}


#######################################################
######################    MAP    ######################
#######################################################

def initMap(mapCharged):
    hauteur = len(mapCharged)
    largeur = len(mapCharged[0])

    carte = [
        ["#" for _ in range(largeur)]
        for _ in range(hauteur)
    ]

    for ligne in range(1, hauteur - 1):
        for colonne in range(1, largeur - 1):
            carte[ligne][colonne] = " "

    return carte


def updateMap(position, perception, carte):
    ligne, colonne = position
    hauteur = len(carte)
    largeur = len(carte[0])
    percues = []

    # Effacer l'ancienne position du robot.
    for rangee in carte:
        for indice, valeur in enumerate(rangee):
            if valeur == "R":
                rangee[indice] = "."

    directions = {
        "N": (-1, 0),
        "S": (1, 0),
        "E": (0, 1),
        "O": (0, -1),
    }

    for direction, (dl, dc) in directions.items():
        l = ligne + dl
        c = colonne + dc

        if not (0 <= l < hauteur and 0 <= c < largeur):
            continue

        if direction not in perception:
            continue

        if carte[l][c] in (" ", "R"):
            carte[l][c] = perception[direction]

        percues.append((l, c))

    carte[ligne][colonne] = "R"

    return carte, percues


def drawMap(canvas, carte, percues, residents):
    canvas.delete("all")

    positions_residents = {
        tuple(resident["position"]): resident["id"]
        for resident in residents
    }

    percues = set(percues)

    for ligne, rangee in enumerate(carte):
        for colonne, case in enumerate(rangee):
            palette = (
                COULEURS_FONCEES
                if (ligne, colonne) in percues
                else COULEURS
            )

            couleur = palette.get(case, "#cccccc")

            x1 = colonne * TAILLE_CASE_AFFICHAGE
            y1 = ligne * TAILLE_CASE_AFFICHAGE
            x2 = x1 + TAILLE_CASE_AFFICHAGE
            y2 = y1 + TAILLE_CASE_AFFICHAGE

            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=couleur,
                outline="#888888",
            )

            if case == "R":
                canvas.create_text(
                    (x1 + x2) // 2,
                    (y1 + y2) // 2,
                    text="R",
                    font=("Arial", 16, "bold"),
                    fill="white",
                )

            elif case == "P":
                identifiant = positions_residents.get(
                    (ligne, colonne), "P"
                )

                canvas.create_text(
                    (x1 + x2) // 2,
                    (y1 + y2) // 2,
                    text=identifiant,
                    font=("Arial", 12, "bold"),
                    fill="white",
                )


#######################################################
######################  ARMOIRE  ######################
#######################################################

def initMapArmoire():
    return [["?" for _ in range(8)] for _ in range(3)]


def updateMapArmoire(coord_casier, map_armoire, contenu):
    intensite, emotion = coord_casier
    map_armoire[intensite][emotion] = contenu
    return map_armoire


def prendreMapArmoire(coord_casier, map_armoire):
    return updateMapArmoire(coord_casier, map_armoire, "")


def drawMapArmoire(canvas, map_armoire, emotions, percues):
    canvas.delete("all")

    hauteur = 3
    largeur = 8
    taille_bloc = 3 * TAILLE_CASE_AFFICHAGE

    largeur_armoire = largeur * taille_bloc
    hauteur_armoire = hauteur * taille_bloc

    canvas.create_rectangle(
        0, 25,
        largeur_armoire, hauteur_armoire + 25,
        fill=COULEURS["A"],
        outline="",
    )

    for ligne in range(hauteur):
        for colonne in range(largeur):
            case = map_armoire[ligne][colonne]

            vue = (
                percues is not None
                and tuple(percues) == (ligne, colonne)
            )

            for sous_ligne in range(3):
                for sous_colonne in range(3):
                    x1 = (
                        colonne * taille_bloc
                        + sous_colonne * TAILLE_CASE_AFFICHAGE
                    )

                    y1 = (
                        ligne * taille_bloc
                        + sous_ligne * TAILLE_CASE_AFFICHAGE
                        + 25
                    )

                    if sous_ligne < 2:
                        remplissage = COULEURS_INTENSITE[ligne]
                    elif vue:
                        remplissage = "#5d4037"
                    else:
                        remplissage = ""

                    canvas.create_rectangle(
                        x1,
                        y1,
                        x1 + TAILLE_CASE_AFFICHAGE,
                        y1 + TAILLE_CASE_AFFICHAGE,
                        fill=remplissage,
                        outline="#888888",
                    )

            x_centre = colonne * taille_bloc + taille_bloc // 2
            y_centre = ligne * taille_bloc + taille_bloc // 2 + 25

            if vue:
                canvas.create_polygon(
                    x_centre - 15, y_centre + 40,
                    x_centre + 15, y_centre + 40,
                    x_centre, y_centre + 12,
                    fill="#ffd166",
                    outline="#3f2d20",
                )

            if case:
                texte = str(case)

                if len(texte) > 8:
                    texte = texte[:7] + "…"

                canvas.create_text(
                    x_centre,
                    y_centre,
                    text=texte,
                    font=("Arial", 12, "bold"),
                    fill="#3f2d20",
                )

    for indice in range(largeur + 1):
        x = indice * taille_bloc

        if indice == 0:
            x = 3

        canvas.create_line(
            x, 25,
            x, hauteur_armoire + 25,
            fill=COULEURS["A"],
            width=3,
        )

    for indice, emotion in enumerate(emotions):
        canvas.create_text(
            indice * taille_bloc + taille_bloc // 2,
            12,
            text=emotion,
            font=("Arial", 11, "bold"),
            fill="black",
        )


#######################################################
#####################  FENÊTRE  #######################
#######################################################

def initDrawing(trace, carte):
    hauteur = len(carte)
    largeur = len(carte[0])

    root = tk.Tk()
    root.title("Visualisation du robot")

    header = tk.Frame(root)
    header.pack(fill="x")

    label_pas = tk.Label(
        header,
        text=f"Pas 0 / {len(trace['pas'])}",
        font=("Arial", 14, "bold"),
    )
    label_pas.pack(side="left", padx=10, pady=5)

    label_liv = tk.Label(
        header,
        text=f"Livraison 0 / {trace['resume']['demandes']}",
        font=("Arial", 14, "bold"),
    )
    label_liv.pack(side="right", padx=10, pady=5)

    zone = tk.Frame(root)
    zone.pack()

    canvas = tk.Canvas(
        zone,
        width=largeur * TAILLE_CASE_AFFICHAGE,
        height=hauteur * TAILLE_CASE_AFFICHAGE,
        bg="white",
    )

    canvas_armoire = tk.Canvas(
        zone,
        width=8 * 3 * TAILLE_CASE_AFFICHAGE,
        height=3 * 3 * TAILLE_CASE_AFFICHAGE + 25,
        bg="white",
    )

    main_frame = tk.Frame(root)
    main_frame.pack(fill="x")

    label_hand = tk.Label(
        main_frame,
        text="Main : vide",
        font=("Arial", 14, "bold"),
    )
    label_hand.pack(side="left", padx=8, pady=8)

    label_action = tk.Label(
        main_frame,
        text="Action : aucune",
        font=("Arial", 14, "bold"),
    )
    label_action.pack(side="right", padx=8, pady=8)

    return (
        root,
        canvas,
        canvas_armoire,
        label_pas,
        label_liv,
        label_hand,
        label_action,
    )


#######################################################
######################   MAIN   #######################
#######################################################

def main(argv):
    if len(argv) != 2:
        print(
            f"Usage : {argv[0]} chemin_trace.json",
            file=sys.stderr,
        )
        return 2

    chemin_trace = Path(argv[1])

    try:
        trace = rio.charger_trace(chemin_trace)

        carte = rio.charger_carte(
            "cartes/" + trace["carte"] + ".json"
        )

        scenario = rio.charger_scenario(
            "scenarios/" + trace["scenario"] + ".json"
        )

        armoire = rio.charger_armoire(
            "donnees/" + scenario["armoire"] + ".json"
        )

    except rio.ErreurFichier as err:
        print(f"erreur de chargement : {err}", file=sys.stderr)
        return 1

    pas = trace["pas"]
    nombre_pas = len(pas)
    residents = carte["residents"]

    (
        root,
        canvas,
        canvas_armoire,
        label_pas,
        label_liv,
        label_hand,
        label_action,
    ) = initDrawing(trace, initMap(carte["grille"]))

    # L'état 0 correspond à la situation avant le premier pas.
    historique = [{
        "carte": initMap(carte["grille"]),
        "armoire": initMapArmoire(),
        "contenu_casiers": [
            deepcopy(casier["objet"])
            for casier in armoire["casiers"]
        ],
        "percues": [],
        "casier": None,
        "dans_armoire": False,
        "main": "vide",
        "livraisons": 0,
    }]

    position = 0
    lecture = False
    minuterie = None

    def action_du_pas(step):
        return str(step.get("action", "")).strip().upper()

    def est_action_importante(step):
        action = action_du_pas(step)

        return bool(action) and action not in {
            "AVANCER",
            "CHERCHER",
        }

    def calculer_etat(etat_precedent, step):
        etat = deepcopy(etat_precedent)
        action = action_du_pas(step)

        if action == "CHERCHER":
            etat["dans_armoire"] = True

        if action == "PRENDRE":
            casier = step["casier"]
            intensite, emotion = casier
            indice_casier = intensite * 8 + emotion

            # Vider le contenu réel et le contenu affiché du casier.
            etat["contenu_casiers"][indice_casier] = ""
            prendreMapArmoire(casier, etat["armoire"])

            etat["casier"] = casier
            etat["main"] = str(step["argument"]).lower()
            etat["dans_armoire"] = False

        elif action == "DONNER":
            etat["main"] = "vide"

            # Comptage conservé depuis le code initial.
            livraisons = trace.get("livraisons", [])
            indice = etat["livraisons"]

            if indice < len(livraisons) and livraisons[indice]:
                etat["livraisons"] += 1

        elif etat["dans_armoire"]:
            casier = step.get("casier")

            if casier is not None:
                intensite, emotion = casier
                indice_casier = intensite * 8 + emotion

                # Utiliser le contenu actuel, pas le contenu initial.
                objet = etat["contenu_casiers"][indice_casier]

                updateMapArmoire(
                    casier,
                    etat["armoire"],
                    objet,
                )

                etat["casier"] = casier

        elif "position" in step and "perception" in step:
            etat["carte"], etat["percues"] = updateMap(
                step["position"],
                step["perception"],
                etat["carte"],
            )

        return etat

    def afficher_etat():
        etat = historique[position]

        label_pas.config(
            text=f"Pas {position} / {nombre_pas}"
        )

        label_liv.config(
            text=(
                f"Livraison {etat['livraisons']} / "
                f"{trace['resume']['demandes']}"
            )
        )

        label_hand.config(text=f"Main : {etat['main']}")

        action = (
            action_du_pas(pas[position - 1])
            if position > 0
            else ""
        )

        label_action.config(
            text=f"Action : {action or 'aucune'}"
        )

        if etat["dans_armoire"]:
            canvas.pack_forget()

            if not canvas_armoire.winfo_manager():
                canvas_armoire.pack(padx=10, pady=10)

            drawMapArmoire(
                canvas_armoire,
                etat["armoire"],
                armoire["emotions"],
                etat["casier"],
            )

        else:
            canvas_armoire.pack_forget()

            if not canvas.winfo_manager():
                canvas.pack(padx=10, pady=10)

            drawMap(
                canvas,
                etat["carte"],
                etat["percues"],
                residents,
            )

        etat_arriere = (
            tk.NORMAL if position > 0 else tk.DISABLED
        )

        etat_avant = (
            tk.NORMAL if position < nombre_pas else tk.DISABLED
        )

        bouton_reculer.config(state=etat_arriere)
        bouton_action_precedente.config(state=etat_arriere)

        bouton_avancer.config(state=etat_avant)
        bouton_action_suivante.config(state=etat_avant)

        # Pause reste disponible pendant une animation.
        bouton_lecture.config(
            text="Pause ⏸" if lecture else "Lecture ▶",
            state=tk.NORMAL if lecture else etat_avant,
        )

    def aller_a(cible):
        nonlocal position

        cible = max(0, min(cible, nombre_pas))

        # Mémoriser les états pour permettre le retour en arrière.
        while len(historique) <= cible:
            indice_pas = len(historique) - 1

            nouvel_etat = calculer_etat(
                historique[-1],
                pas[indice_pas],
            )

            historique.append(nouvel_etat)

        position = cible
        afficher_etat()

    def pause():
        nonlocal lecture, minuterie

        lecture = False

        if minuterie is not None:
            root.after_cancel(minuterie)
            minuterie = None

        bouton_lecture.config(
            text="Lecture ▶",
            state=(
                tk.NORMAL
                if position < nombre_pas
                else tk.DISABLED
            ),
        )

    def delai_etat_courant():
        delai = DELAI_AFFICHAGE

        if position > 0:
            action = action_du_pas(pas[position - 1])

            if (
                historique[position]["dans_armoire"]
                or action == "PRENDRE"
            ):
                delai += DELAI_AFFICHAGE * 5

        return delai

    def avancer():
        pause()
        aller_a(position + 1)

    def reculer():
        pause()
        aller_a(position - 1)

    def animer_jusqua(cible):
        nonlocal lecture, minuterie

        pause()

        cible = max(0, min(cible, nombre_pas))

        if cible == position:
            return

        direction = 1 if cible > position else -1

        lecture = True

        bouton_lecture.config(
            text="Pause ⏸",
            state=tk.NORMAL,
        )

        def etape():
            nonlocal minuterie

            minuterie = None

            if not lecture:
                return

            aller_a(position + direction)

            if position == cible:
                pause()
                return

            minuterie = root.after(
                delai_etat_courant(),
                etape,
            )

        etape()

    def action_suivante():
        cible = nombre_pas

        for indice in range(position, nombre_pas):
            if est_action_importante(pas[indice]):
                cible = indice + 1
                break

        animer_jusqua(cible)

    def action_precedente():
        cible = 0

        # Ignorer le pas actuellement affiché.
        for indice in range(position - 2, -1, -1):
            if est_action_importante(pas[indice]):
                cible = indice + 1
                break

        animer_jusqua(cible)

    def basculer_lecture():
        if lecture:
            pause()
        else:
            animer_jusqua(nombre_pas)

    def fermer():
        pause()
        root.destroy()

    controles = tk.Frame(root)
    controles.pack(fill="x", padx=10, pady=10)

    bouton_reculer = tk.Button(
        controles,
        text="← Pas",
        command=reculer,
    )

    bouton_avancer = tk.Button(
        controles,
        text="Pas →",
        command=avancer,
    )

    bouton_action_precedente = tk.Button(
        controles,
        text="← Action",
        command=action_precedente,
    )

    bouton_action_suivante = tk.Button(
        controles,
        text="Action →",
        command=action_suivante,
    )

    bouton_lecture = tk.Button(
        controles,
        text="Lecture ▶",
        command=basculer_lecture,
    )

    for bouton in (
        bouton_reculer,
        bouton_avancer,
        bouton_action_precedente,
        bouton_action_suivante,
        bouton_lecture,
    ):
        bouton.pack(
            side="left",
            expand=True,
            fill="x",
            padx=3,
        )

    root.protocol("WM_DELETE_WINDOW", fermer)

    afficher_etat()
    root.mainloop()

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))