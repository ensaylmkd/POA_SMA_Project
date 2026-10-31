"""pour lancer : python -m unittest discover -s test -v"""
import unittest
from Environment import *
from affichage import *
from Explorer import *
from parcours import *
import reconfort_io as rio
from MouvementDansArmoire import *
from MouvementDansMap import *
import consultDico as cd
from src.agentExemple import *

appartement = [
    ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],  # 0
    ['#', '.', '.', '.', '.', 'D', '.', 'P', '.', '.', 'A', '#'],  # 1
    ['#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#'],  # 2
    ['#', '#', '#', '#', '#', '.', '#', '#', '#', '#', '.', '#'],  # 3
    ['#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#'],  # 4
    ['#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#'],  # 5
    ['#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#'],  # 6
    ['#', '#', '#', '#', '#', '#', '#', '.', '#', '#', '#', '#'],  # 7
    ['#', '.', '.', '.', '.', '.', '.', '.', '#', '.', '.', '#'],  # 8
    ['#', '.', '.', '.', '.', 'P', '#', '.', '#', '.', 'P', '#'],  # 9
    ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#']   # 10
]    #0    1    2    3    4    5    6    7    8    9    10   11  
R = (5,5)
D = (1,5)
A = (1,10)
R1 = (1,7)
R2 = (9,5)
R3 = (9, 10)

armoire_vide  = {
  "format": "robot-reconfort/armoire",
  "version": 1,
  "nom": "armoire_standard",
  "emotions": [
    "joie",
    "confiance",
    "peur",
    "surprise",
    "tristesse",
    "degout",
    "colere",
    "anticipation"
  ],
  "intensites": [
    "faible",
    "moyenne",
    "forte"
  ],
  "casier_depart": [
    1,
    0
  ],
  "casiers": [
    {
      "ligne": 0,
      "colonne": 0,
      "emotion": "joie",
      "intensite": "faible",
      "objet": None
    },
    {
      "ligne": 0,
      "colonne": 1,
      "emotion": "confiance",
      "intensite": "faible",
      "objet": None
    },
    {
      "ligne": 0,
      "colonne": 2,
      "emotion": "peur",
      "intensite": "faible",
      "objet": None
    },
    {
      "ligne": 0,
      "colonne": 3,
      "emotion": "surprise",
      "intensite": "faible",
      "objet": None
    },
    {
      "ligne": 0,
      "colonne": 4,
      "emotion": "tristesse",
      "intensite": "faible",
      "objet": None
    },
    {
      "ligne": 0,
      "colonne": 5,
      "emotion": "degout",
      "intensite": "faible",
      "objet": None
    },
    {
      "ligne": 0,
      "colonne": 6,
      "emotion": "colere",
      "intensite": "faible",
      "objet": None
    },
    {
      "ligne": 0,
      "colonne": 7,
      "emotion": "anticipation",
      "intensite": "faible",
      "objet": None
    },
    {
      "ligne": 1,
      "colonne": 0,
      "emotion": "joie",
      "intensite": "moyenne",
      "objet": None
    },
    {
      "ligne": 1,
      "colonne": 1,
      "emotion": "confiance",
      "intensite": "moyenne",
      "objet": None
    },
    {
      "ligne": 1,
      "colonne": 2,
      "emotion": "peur",
      "intensite": "moyenne",
      "objet": None
    },
    {
      "ligne": 1,
      "colonne": 3,
      "emotion": "surprise",
      "intensite": "moyenne",
      "objet": None
    },
    {
      "ligne": 1,
      "colonne": 4,
      "emotion": "tristesse",
      "intensite": "moyenne",
      "objet": None
    },
    {
      "ligne": 1,
      "colonne": 5,
      "emotion": "degout",
      "intensite": "moyenne",
      "objet": None
    },
    {
      "ligne": 1,
      "colonne": 6,
      "emotion": "colere",
      "intensite": "moyenne",
      "objet": None
    },
    {
      "ligne": 1,
      "colonne": 7,
      "emotion": "anticipation",
      "intensite": "moyenne",
      "objet": None
    },
    {
      "ligne": 2,
      "colonne": 0,
      "emotion": "joie",
      "intensite": "forte",
      "objet": None
    },
    {
      "ligne": 2,
      "colonne": 1,
      "emotion": "confiance",
      "intensite": "forte",
      "objet": None
    },
    {
      "ligne": 2,
      "colonne": 2,
      "emotion": "peur",
      "intensite": "forte",
      "objet": None
    },
    {
      "ligne": 2,
      "colonne": 3,
      "emotion": "surprise",
      "intensite": "forte",
      "objet": None
    },
    {
      "ligne": 2,
      "colonne": 4,
      "emotion": "tristesse",
      "intensite": "forte",
      "objet": None
    },
    {
      "ligne": 2,
      "colonne": 5,
      "emotion": "degout",
      "intensite": "forte",
      "objet": None
    },
    {
      "ligne": 2,
      "colonne": 6,
      "emotion": "colere",
      "intensite": "forte",
      "objet": None
    },
    {
      "ligne": 2,
      "colonne": 7,
      "emotion": "anticipation",
      "intensite": "forte",
      "objet": None
    }
  ]
}

#1. la planification : sur une petite grille écrite à la main, un chemin dont vous connaissez la longueur ;
class TestParcours(unittest.TestCase):
    def test_deplacement(self) :
       chemin = deplacement(R, (2,5), appartement)
       self.assertEqual(chemin, [(5,5), (4,5), (3,5), (2,5)])
    #Pour déplacement, on ne peut pas mettre une coor qui contient la position d'un objet
       
    def test_deplacement_mur(self) :#si y a un mur dans le chemin + c le chemin opti
        chemin = deplacement(R, (8,5), appartement)
        self.assertEqual(chemin, [(5,5), (5,6), (5,7), (6,7), (7,7), (8,7), (8,6), (8,5)])
        
    def test_deplacement_meme_position(self):
        chemin = deplacement(R, R, appartement)
        self.assertEqual(chemin, [R])

    def test_deplacement_destination_inaccessible(self):
        chemin = deplacement(R, (7, 5), appartement)
        self.assertEqual(chemin, [])

    def test_direction_nord(self):#si nord marche, les autres aussi
        self.assertEqual(direction((5, 5), (4, 5)), ["AVANCER", "N"])

#2. la replanification : un mur découvert en route change le trajet ;
#On va juste tester l'exploration et voir si il arrive à générer la bonne map
class TestExplorer(unittest.TestCase):
    carte_robot =[
        ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],  # 0
        ['#', '.', '.', '.', '.', 'D', '.', 'P', '.', '.', 'A', '#'],  # 1
        ['#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#'],  # 2
        ['#', '#', '#', '#', '#', '.', '#', '#', '#', '#', '.', '#'],  # 3
        ['#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#'],  # 4
        ['#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#'],  # 5
        ['#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#'],  # 6
        ['#', '#', '#', '#', '#', '#', '#', '.', '#', '#', '#', '#'],  # 7
        ['#', '.', '.', '.', '.', '.', '.', '.', '#', '?', '?', '#'],  # 8
        ['#', '.', '.', '.', '.', 'P', '#', '.', '#', '?', '?', '#'],  # 9 le P ici ne peut être rencontrer
        ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#']   # 10
    ] 
    def test_exploration_complete(self):
        carte = appartement
        hauteur = len(carte)
        largeur = len(carte[0])

        # Faux agent : il ne donne que sa position et sa perception.
        class FauxAgent:
            def __init__(self, position):
                self.newinfo = {}
                self.position = position
            def actualiser(self):
                x, y = self.position
                self.newinfo = {
                    "posTerrain": self.position,
                    "perception": {
                        "N": carte[x-1][y],
                        "S": carte[x+1][y],
                        "E": carte[x][y+1],
                        "O": carte[x][y-1]
                    }
                }

        agent = FauxAgent(R)
        explorer = Explorer(agent, {"hauteur": hauteur, "largeur": largeur})
        directions = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "O": (0, -1)}
        max_iterations = 1000
        iterations = 0
        while not explorer.is_finish and iterations < max_iterations:
            agent.actualiser()
            explorer.updateState()
            action = explorer.nextAction()
            if action[0] == "ATTENDRE":
                break
            self.assertEqual(action[0], "AVANCER")
            dx, dy = directions[action[1]]
            x, y = agent.position
            nouvelle_position = (x + dx, y + dy)
            # Vérification que le robot ne traverse pas un mur (devrait pas arriver)
            self.assertEqual(carte[nouvelle_position[0]][nouvelle_position[1]], ".")
            agent.position = nouvelle_position
            iterations += 1
        # Vérifications de l'attribut is_finish (+ que ça finit)
        self.assertTrue(explorer.is_finish)
        self.assertLess(iterations, max_iterations)
        #les cartes doivent être identique avec le P en bas à droite qui serait '?' car enmuré        
        self.assertEqual(explorer.carte_mental, self.carte_robot)

#3.la lecture du dictionnaire : un message par émotion, plus un message où deux mots connus apparaissent et où c'est bien le premier qui gagne, plus un message sans aucun mot reconnu ;
class TestDictionnaire(unittest.TestCase):

    def test_aucun_mot_reconnu(self):
        message = "zxqvplmok"
        self.assertIsNone(cd.EmotionInfoFromSentence(message))

    def test_find_emotion_intensite(self) :
        scenario_message = {"demandes": [{"numero": 1,"message": "Je suis sidéré, la télévision s'est allumée toute seule."},
                                         {"numero": 2, "message": "Je suis furieux, on a encore oublié mon repas."},
                                         {"numero": 3, "message": "Je me sens calme, la matinée était tranquille."}]}#calme et tranquille dans dictionnaire
        list_resultat = []
        for demande in scenario_message["demandes"]:
            message=demande["message"]
            message_norm = cd.normaliser(message)
            resultat = cd.findEmotionIntensite(message_norm)
            list_resultat.append(resultat)
        self.assertTrue(list_resultat[0], ["surprise", "forte"])
        self.assertTrue(list_resultat[1], ["colère", "forte"])
        self.assertTrue(list_resultat[2], ["joie", "faible"])

#4. le déplacement du sélecteur dans l'armoire, y compris le bouclage entre la colonne 7 et la colonne 0 ;
class TestArmoire(unittest.TestCase):
    agent = None
    mouvement = MouvementDansArmoire(agent, (3, 7), "joie", "moyenne") #"objet": "photo de famille", ligne : 1 colonne : 0

    def test_deplacement_vertical(self):#si ça marche les autres marchent
        self.assertEqual(self.mouvement.deplacerDansArmoire((1, 0), (0, 0)), ["N"])

    def test_deplacement_horizontal(self):#Pour plus de dplacements
        self.assertEqual(self.mouvement.deplacerDansArmoire((1, 0), (1, 3)), ["E", "E", "E"])

    def test_bouclage_colonne_7_vers_0(self):
        self.assertEqual(self.mouvement.deplacerDansArmoire((1, 7), (1, 0)), ["E"])

    def test_bouclage_colonne_0_vers_7(self):
        self.assertEqual(self.mouvement.deplacerDansArmoire((1, 0), (1, 7)), ["O"])

    def test_chemin_horizontal_le_plus_court(self):#pour voir si on passe par la gauche plutôt que de faire plein de saut à droite
        self.assertEqual(self.mouvement.deplacerDansArmoire((1, 1), (1, 7)), ["O", "O"])

    #5. la règle de repli : casier exact garni, casier vide avec repli en intensité, colonne entière vide avec repli sur une voisine, aucun casier garni à distance ≤ 2 ;
    class FauxAgent:
        def __init__(self):
            self.newinfo = {}

#6. la validation des fichiers : un fichier cassé par catégorie de la section 5.6 ;

#7. le cas inaccessible : un résident muré, sur une grille minuscule écrite à la main.

if __name__ == "__main__":
  unittest.main()