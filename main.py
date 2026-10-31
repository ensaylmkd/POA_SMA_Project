"""
python3 -m main cartes/appartement_01.json scenarios/scenario_03.json donnees sorties/trace_test.json
"""

import sys
from pathlib import Path

import reconfort_io as rio
from src.Environment import *


# ====================== Constantes ==============================

EMOTIONS = [
    "joie", "confiance", "peur", "surprise",
    "tristesse", "degout", "colere", "anticipation"
]
INTENSITES = ["faible", "moyenne", "forte"]


# ====================== Validation Utils ==============================

def verifier(condition, message):
    if not condition:
        raise rio.ErreurFichier(message)


def verifierPosition(pos, h, l):
    verifier(
        type(pos) is list and len(pos) == 2
        and all(type(v) is int for v in pos),
        f"position invalide : {pos}"
    )
    verifier(
        0 <= pos[0] < h and 0 <= pos[1] < l,
        f"position hors limites : {pos}"
    )


# ====================== Validation des fichiers ==============================

def verifierFichiers(carte, scenario, dico, armoire):

    for data in [carte, scenario, dico, armoire]:
        verifier(type(data["nom"]) is str, "nom de fichier invalide")
        verifier(
            type(data["version"]) is int
            and data["version"] == rio.VERSION_ATTENDUE,
            "version de fichier incorrecte"
        )

    # ====================== Carte ==============================
    h = carte["dimensions"]["hauteur"]
    l = carte["dimensions"]["largeur"]
    grille = carte["grille"]

    verifier(
        type(h) is int and type(l) is int and h > 0 and l > 0,
        "carte : dimensions invalides"
    )
    verifier(
        type(grille) is list and len(grille) == h
        and all(type(ligne) is str and len(ligne) == l for ligne in grille),
        "carte : grille non rectangulaire ou dimensions incohérentes"
    )

    positions = [
        (carte["depart_robot"], "R"),
        (carte["armoire"]["position"], "A"),
        (carte["dictionnaire"]["position"], "D")
    ]
    positions += [(r["position"], "P") for r in carte["residents"]]

    for pos, symbole in positions:
        verifierPosition(pos, h, l)
        verifier(
            grille[pos[0]][pos[1]] == symbole,
            f"carte : symbole '{symbole}' attendu en {pos}"
        )

    ids = [r["id"] for r in carte["residents"]]
    verifier(len(ids) == len(set(ids)), "carte : identifiant résident en double")

    # ====================== Scénario ==============================
    verifier(scenario["carte"] == carte["nom"], "scénario : mauvaise carte")
    verifier(scenario["armoire"] == armoire["nom"], "scénario : mauvaise armoire")

    for demande in scenario["demandes"]:
        verifier(
            demande["resident"] in ids,
            f"demande : résident '{demande['resident']}' absent"
        )
        verifier(
            type(demande["numero"]) is int and type(demande["message"]) is str,
            "demande : numéro ou message invalide"
        )

    # ====================== Dictionnaire ==============================
    for data in [dico, armoire]:
        verifier(
            data["emotions"] == EMOTIONS and data["intensites"] == INTENSITES,
            "dictionnaire ou armoire : émotions / intensités incorrectes"
        )

    motsVus = {}

    for i, entree in enumerate(dico["entrees"]):
        verifier(
            entree["emotion"] in EMOTIONS and entree["intensite"] in INTENSITES,
            "dictionnaire : émotion ou intensité inconnue"
        )

        for forme in entree["formes"]:
            mots = rio.normaliser(forme)
            verifier(len(mots) == 1, "dictionnaire : forme invalide")
            mot = mots[0]

            verifier(
                mot not in motsVus or motsVus[mot] == i,
                f"dictionnaire : mot '{mot}' dans deux entrées"
            )
            motsVus[mot] = i

    # ====================== Armoire ==============================
    verifierPosition(armoire["casier_depart"], 3, 8)
    positionsVues = set()

    for casier in armoire["casiers"]:
        x, y = casier["ligne"], casier["colonne"]

        verifierPosition([x, y], 3, 8)
        verifier((x, y) not in positionsVues, f"casier {(x, y)} en double")
        positionsVues.add((x, y))

        verifier(
            casier["emotion"] == EMOTIONS[y]
            and casier["intensite"] == INTENSITES[x],
            f"casier {(x, y)} : mauvaise émotion ou intensité"
        )
        verifier(
            casier["objet"] is None or type(casier["objet"]) is str,
            f"casier {(x, y)} : objet invalide"
        )

    verifier(len(positionsVues) == 24, "armoire : casiers manquants")
    armoire["casiers"].sort(key=lambda elt: (elt["ligne"], elt["colonne"]))


# ====================== MAIN ==============================

def main(argv):

    # ====================== Arguments ==============================
    if len(argv) != 5:
        print(__doc__.strip(), file=sys.stderr)
        return 2

    chemin_carte, chemin_scenario = Path(argv[1]), Path(argv[2])
    dossier_donnees, chemin_sortie = Path(argv[3]), Path(argv[4])

    # ====================== Lecture et validation ==============================
    try:
        carte = rio.charger_carte(chemin_carte)
        scenario = rio.charger_scenario(chemin_scenario)
        dictionnaire = rio.charger_dictionnaire(
            dossier_donnees / "dictionnaire.json"
        )

        verifier(
            type(scenario["armoire"]) is str,
            "scénario : nom d'armoire invalide"
        )
        armoire = rio.charger_armoire(
            dossier_donnees / f"{scenario['armoire']}.json"
        )

        verifierFichiers(carte, scenario, dictionnaire, armoire)

    except rio.ErreurFichier as err:
        print(f"erreur de chargement : {err}", file=sys.stderr)
        return 1

    except KeyError as err:
        print(f"erreur : champ obligatoire absent {err}", file=sys.stderr)
        return 1

    except (TypeError, ValueError, IndexError, AttributeError):
        print(
            "erreur : structure ou type de champ invalide dans les fichiers",
            file=sys.stderr
        )
        return 1

    # ==========================================================================
    # ====================== Simulation ==============================

    trace = rio.Trace(
        nom_carte=carte["nom"],
        nom_scenario=scenario["nom"],
        equipe=["FAURON Quentin", "LAMKADDEM Yassine", "THOMAS Lucas"]
    )

    env = Environment(carte, scenario, dictionnaire, armoire, trace)
    env.run()

    # ====================== Écriture ==============================

    try:
        trace.ecrire(chemin_sortie)
    except OSError as err:
        print(f"erreur d'écriture de la trace : {err}", file=sys.stderr)
        return 1

    print(f"\ntrace ecrite : {chemin_sortie}")
    return 0


# ==========================================================
if __name__ == "__main__":
    raise SystemExit(main(sys.argv))