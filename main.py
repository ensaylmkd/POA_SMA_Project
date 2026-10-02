"""
python3 main.py cartes/appartement_01.json scenarios/scenario_01.json donnees sorties/trace_01.json
"""

import sys
from pathlib import Path

import reconfort_io as rio
from Environment import *


def main(argv):

    # ====================== LECTURE DES FICHIERS ==============================
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

    # ==========================================================================

    # ====================== MAIN ==============================

    env = Environment(carte,scenario,dictionnaire,armoire)
    print(env)

    agentInfo = env.get_initAgent_info()
    for key in agentInfo.keys():
        print(key, agentInfo[key])
    print()

    x,y = 6,1
    print(env.carte["grille"][x])

    print(env.get_perception(x,y))

    print("carte")

    for i in range(len(carte["grille"])):
        print(carte["grille"][i])
    return 0


    # ==========================================================
    

    # trace = rio.Trace(
    #     nom_carte=carte["nom"],
    #     nom_scenario=scenario["nom"],
    #     equipe=["A completer", "A completer"],
    # )

    # for demande in scenario["demandes"]:
    #     numero = demande["numero"]
    #     print(f"\ndemande {numero} ({demande['resident']}) : "
    #           f"{demande['message']}")
    #     print(f"  mots normalises : {rio.normaliser(demande['message'])}")

    #     trace.ajouter_pas(
    #         demande=numero,
    #         position=carte["depart_robot"],
    #         casier=armoire["casier_depart"],
    #         action="ATTENDRE",
    #         commentaire="robot de demonstration : ne fait rien",
    #     )
    #     trace.ajouter_livraison(
    #         demande=numero,
    #         resident=demande["resident"],
    #         emotion=None,
    #         intensite=None,
    #         casier_choisi=None,
    #         repli="aucun",
    #         objet=None,
    #         succes=False,
    #         motif_echec="agent non implemente",
    #     )

    # trace.ecrire(chemin_sortie)
    # print(f"\ntrace ecrite : {chemin_sortie}")

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
