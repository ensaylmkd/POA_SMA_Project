
import unittest

from Environment import *
from parcours import deplacement, parcours_map


# Carte de test fournie dans l'énoncé
CARTE = {
    "format": "robot-reconfort/carte",
    "version": 1,
    "nom": "appartement_01",
    "dimensions": {
        "hauteur": 9,
        "largeur": 13
    },
    "grille": [
        "#############",
        "#......#....#",
        "#...........#",
        "#..P...#....#",
        "#.#########.#",
        "#......#....#",
        "#R..A..#...P#",
        "#.....D#....#",
        "#############"
    ],
    "depart_robot": [6, 1],
    "armoire": {"position": [6, 4]},
    "dictionnaire": {"position": [7, 6]},
    "residents": [
        {"id": "R1", "nom": "Camille", "position": [6, 11]},
        {"id": "R2", "nom": "Hugo", "position": [3, 3]}
    ]
}

ARMOIRE = {
    "casier_depart": [1, 0],
    "casiers": []
}

SCENARIO = {}
DICTIONNAIRE = {"position": [7, 6]}


def creer_environnement():
    """Crée un nouvel environnement pour chaque test."""
    carte = {
        **CARTE,
        "grille": list(CARTE["grille"]),
        "depart_robot": list(CARTE["depart_robot"]),
        "dimensions": dict(CARTE["dimensions"]),
        "armoire": dict(CARTE["armoire"]),
        "dictionnaire": dict(CARTE["dictionnaire"]),
        "residents": list(CARTE["residents"])
    }

    return Environment(
        carte,
        SCENARIO,
        DICTIONNAIRE,
        ARMOIRE
    )


class TestParcours(unittest.TestCase):

    def test_bfs_trouve_un_chemin(self):
        """Le BFS doit trouver un chemin valide jusqu'à une case libre."""
        env = creer_environnement()

        # Carte connue pour ce test uniquement.
        # On remplace R par "." car c'est la position du robot.
        grille = [list(ligne) for ligne in CARTE["grille"]]
        grille[6][1] = "."

        depart = (6, 1)
        but = (6, 5)

        chemin = deplacement(depart, but, grille)

        self.assertTrue(chemin, "Aucun chemin trouvé")
        self.assertEqual(chemin[0], depart)
        self.assertEqual(chemin[-1], but)

        # Vérifie chaque déplacement et chaque case traversée.
        for a, b in zip(chemin, chemin[1:]):
            distance = abs(a[0] - b[0]) + abs(a[1] - b[1])

            self.assertEqual(distance, 1, "Déplacement non adjacent")
            self.assertEqual(
                grille[b[0]][b[1]],
                ".",
                f"Le chemin traverse une case interdite : {b}"
            )

        print("\nChemin BFS :", chemin)
        print("Longueur du chemin :", len(chemin) - 1)

    def test_bfs_sans_chemin(self):
        """Le BFS doit renvoyer [] si l'objectif est inaccessible."""
        grille = [
            list("#####"),
            list("#.#.#"),
            list("#####")
        ]

        depart = (1, 1)
        but = (1, 3)

        chemin = deplacement(depart, but, grille)

        self.assertEqual(chemin, [])

    def test_bfs_depart_egal_but(self):
        """Le chemin vers sa propre position contient une seule case."""
        env = creer_environnement()

        grille = [list(ligne) for ligne in CARTE["grille"]]
        grille[6][1] = "."

        # Nécessite le correctif proposé dans la réponse précédente.
        chemin = deplacement((6, 1), (6, 1), grille)

        self.assertEqual(chemin, [(6, 1)])

    def test_exploration_carte(self):
        """Le robot doit explorer et mémoriser les cases accessibles."""
        env = creer_environnement()
        agent = env.agents[0]

        hauteur = CARTE["dimensions"]["hauteur"]
        largeur = CARTE["dimensions"]["largeur"]

        # '?' signifie inconnu.
        carte_mentale = [
            ["?" for _ in range(largeur)]
            for _ in range(hauteur)
        ]

        depart = tuple(CARTE["depart_robot"])
        carte_mentale[depart[0]][depart[1]] = "."

        # La fonction déplace réellement le robot grâce à mouvement().
        resultat = parcours_map(
    depart,
    carte_mentale,
    agent,
    env
)

        position_finale = tuple(env.agentsPosTerrain[0])

        self.assertEqual(len(resultat), hauteur)
        self.assertTrue(
            0 <= position_finale[0] < hauteur
            and 0 <= position_finale[1] < largeur
        )

        # La position finale doit être une case intérieure.
        self.assertNotIn(position_finale[0], (0, hauteur - 1))
        self.assertNotIn(position_finale[1], (0, largeur - 1))

        # La carte mentale doit avoir appris au moins une case.
        connues = [
            case
            for ligne in resultat
            for case in ligne
            if case in (".", "#")
        ]

        self.assertGreater(
            len(connues), 1,
            "La carte mentale n'a pratiquement pas été renseignée"
        )

        print("\nCarte mentale obtenue :")
        for ligne in resultat:
            print("".join(ligne))

        print("Position finale :", position_finale)
        print("Nombre de cases connues :", len(connues))


if __name__ == "__main__":
    unittest.main(verbosity=2)
