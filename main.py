"""
python3 -m main cartes/appartement_01.json scenarios/scenario_03.json donnees sorties/trace_test.json
"""

import sys
from pathlib import Path

import reconfort_io as rio
from src.Environment import *


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
    trace = rio.Trace(
        nom_carte=carte["nom"],
        nom_scenario=scenario["nom"],
        equipe=["FAURON Quentin","LAMKADDEM Yassine", "THOMAS Lucas"]
     )

    env = Environment(carte,scenario,dictionnaire,armoire,trace)
    env.run()
    
    trace.ecrire(chemin_sortie)
    print(f"\ntrace ecrite : {chemin_sortie}")

    return 0


    # ==========================================================
if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
