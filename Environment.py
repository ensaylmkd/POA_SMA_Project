class Environment:
    def __init__(self, carte, scenario, dictionnaire, armoire):
        self.carte = carte
        self.scenario = scenario
        self.dictionnaire = dictionnaire
        self.armoire = armoire

        self.agent = []
    

    # Ce que voit le robot au depart : sa position, celle de l'armoire, celle
    # du dictionnaire, et celles des residents. Les murs, eux, ne sont PAS
    # connus a priori, et le contenu des casiers non plus (enonce 3.2 et 3.3).
    # Ne lisez ni carte["grille"], ni le champ "objet" des casiers : votre
    # agent n'y a pas droit.
    def get_initAgent_info(self):
        """ Exemple :
        departRobot   : [6, 1]
        armoire        : [6, 4]
        dictionnaire   : [7, 6]
        casier depart  : [1, 0] 
        """
        return {"departRobot": self.carte['depart_robot'], 
                "armoirePos": self.carte['armoire']['position'],
                "dictionnairePos": self.carte['dictionnaire']['position'],
                "departCasier": self.armoire['casier_depart']
                 }
        
    def get_perception(self,x,y):
        hauteur,largeur = self.carte["dimensions"].values()
        if (x >= hauteur and x > 0) or (y >= largeur and y > 0) :
            print("[ENVIRONMENT][get_perception][error] x or y out of range")
            return None
        N = self.carte["grille"][x-1][y]
        S = self.carte["grille"][x+1][y]
        E = self.carte["grille"][x][y+1]
        O = self.carte["grille"][x][y-1]
        return{ "N":N, 
                "S":S, 
                "E":E,
                "O":O }



    def __str__(self):
        """ Affiche toute les info de l'environment.
        C'est pas si beau mais c'est bine pour debug si besoin """

        print("============== Carte :================")
        for key in self.carte.keys():
            print(f"\t{key}: ",self.carte[key])
        print("============== Scénario: ==============")
        for key in self.scenario.keys():
            print(f"\t{key}: ",self.scenario[key])
        print("======= Dictionnaire :============")
        for key in self.dictionnaire.keys():
            print(f"\t{key}: ",self.dictionnaire[key])
        print("======= Armoire :============")
        for key in self.armoire.keys():
            print(f"\t{key}: ",self.armoire[key])
        return ""


