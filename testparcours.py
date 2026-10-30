from Explorer import *
from Environment import *
import json

carte = "./cartes/appartement_01.json"
scenario = "./scenarios/scenario_03.json"
dictionnaire = "./donnees/dictionnaire.json"
armoire = "./donnees/armoire_standard.json"

with open(carte, "r", encoding="utf-8") as f:
    carte = json.load(f)

with open(scenario, "r", encoding="utf-8") as f:
    scenario = json.load(f)

with open(dictionnaire, "r", encoding="utf-8") as f:
    dictionnaire = json.load(f)

with open(armoire, "r", encoding="utf-8") as f:
    armoire = json.load(f)


def test():
    # Carte réelle : # = mur, . = case accessible
    carte_reelle = [
        list("#######"),
        list("#.....#"),
        list("#.###.#"),
        list("#.....#"),
        list("#######")
    ]

    # Carte mentale initialement inconnue
    carte_mentale = [
        list("#######"),
        list("#?????#"),
        list("#?###?#"),
        list("#?????#"),
        list("#######")
    ]

    # Position de départ
    pos = (1, 1)

    explorer = Explorer(pos, carte_mentale)

    # Simulation de l'exploration
    for i in range(100):

        # On récupère la perception réelle des voisins
        x, y = pos

        newinfo = {
            "perception": {
                "N": carte_reelle[x-1][y],
                "S": carte_reelle[x+1][y],
                "E": carte_reelle[x][y+1],
                "O": carte_reelle[x][y-1]
            }
        }

        # L'explorateur choisit son déplacement
        action = explorer.functionExplorer(pos, newinfo)

        print("etape i : ",i)
        print("Position :", pos)
        print("Action :", action)

        # Si l'exploration est terminée
        if action[0] == "ATTENDRE":
            print("Exploration terminée !")
            break

        # On actualise la position selon la direction
        if action[1] == "HAUT":
            pos = (x-1, y)
        elif action[1] == "BAS":
            pos = (x+1, y)
        elif action[1] == "GAUCHE":
            pos = (x, y-1)
        elif action[1] == "DROITE":
            pos = (x, y+1)

        # Vérification : le robot ne traverse pas de mur
        assert carte_reelle[pos[0]][pos[1]] == ".", \
            "ERREUR : le robot a essayé de traverser un mur !"

    print("\nCarte mentale finale :")
    for ligne in explorer.carte_mental:
        print("".join(ligne))

def test_exploration(environment, max_steps=500):

    agent = environment.agents[0]

    print("\n========== DEBUT DU TEST ==========")

    for i in range(max_steps):

        # Position avant le déplacement
        ancienne_pos = tuple(environment.agentsPosTerrain[0])

        # On récupère la prochaine action et on l'exécute
        environment.timeStep()

        nouvelle_pos = tuple(environment.agentsPosTerrain[0])
        action = agent.nextMove

        print(f"\nEtape {i+1}")
        print("Position :", ancienne_pos)
        print("Action :", action)
        print("Nouvelle position :", nouvelle_pos)

        # Vérification que le déplacement est valide
        distance = (
            abs(nouvelle_pos[0] - ancienne_pos[0])
            + abs(nouvelle_pos[1] - ancienne_pos[1])
        )

        assert distance <= 1, "Le robot a effectué un déplacement invalide"

        # Vérification que le robot n'a pas traversé un mur
        assert environment.grid[nouvelle_pos[0]][nouvelle_pos[1]] != "#", \
            "Le robot a traversé un mur !"

        # Affichage de la carte mentale
        print("\nCarte mentale :")
        for ligne in agent.carte_mental:
            print("".join(ligne))

        # Fin de l'exploration
        if agent.explorer.is_finish:
            print("\n========== EXPLORATION TERMINEE ==========")
            print("Nombre de déplacements :", i+1)
            return True

    print("\nERREUR : nombre maximal d'étapes atteint.")
    return False
environment = Environment(carte, scenario, dictionnaire, armoire)

test_exploration(environment)