emotions = [
        "joie",
        "confiance",
        "peur",
        "surprise",
        "tristesse",
        "degout",
        "colere",
        "anticipation"
    ]
intensites = [
    "faible",
    "moyenne",
    "forte"
]

class MouvementDansArmoire:
    def __init__(self, agent, posDepart, emotionVoulu, intensiteVoulu):
        self.agent = agent

        intensiteIndex = intensites.index(intensiteVoulu)
        emotionIndex = emotions.index(emotionVoulu)
        self.candidats = self.findCandidat(intensiteIndex, emotionIndex)
        self.bestcandidat = self.candidats.pop(0)
        self.mouvements = self.deplacerDansArmoire(posDepart,self.bestcandidat)
        
        self.posCurseur = None
        self.objetVu = None

        self.casierchoisi = None
        self.object = None
        self.repli = None

    def deplacerDansArmoire(self,posDepart, posArrivee):
        '''Calcul la liste des mouvements que le curseur doit faire pour arriver à une position'''
        l, c = posDepart
        l2, c2 = posArrivee

        listDeplacements = []

        # mouvements verticaux
        nbMouvVert = abs(l2 - l)
        for i in range(nbMouvVert):
            if l2 > l:
                listDeplacements.append('S')
            else:
                listDeplacements.append('N')

        # mouvements horizontaux qui loop
        a = (c2-c) % 8
        if a <= 8-a:
            for i in range(a):
                listDeplacements.append('E')
        else:
            for i in range(8-a):
                listDeplacements.append('O')

        return listDeplacements

    def findCandidat(self, intensiteVoulue, emotionVoulue):
        '''Trouve la liste des casiers candidats pour une emotion et une intensité données'''
        intensites_triees = sorted([0,1,2], key=lambda i: abs(i - intensiteVoulue)) # ecart d'intensité croissant (2.) (si égalité alors ordre croissant (3.) )
        
        candidats = []
        
        for distance in range(3): # d(e, e') croissante inférieure ou égale à 2 (1.)
            if distance == 0: # meme emotion
                emotions_candidates = [emotionVoulue]
            else:
                emotions_candidates = [
                    (emotionVoulue + distance) % 8, # horaire       (4.)
                    (emotionVoulue - distance) % 8  # anti-horaire
                ]

            for i in intensites_triees:
                for e in emotions_candidates:
                    candidats.append([i, e])
        
        return candidats

    def updateState(self):
        if self.mouvements == []:
            self.objetVu = self.agent.newinfo['contenu_casier']['objet']
            self.posCurseur = self.agent.newinfo['posCasier']
            if self.objetVu is None and self.candidats:
                candidatTraite = self.candidats.pop(0)
                self.mouvements = self.deplacerDansArmoire(self.posCurseur, candidatTraite)

    def nextAction(self): 
        if self.mouvements != []:
            return ["CHERCHER",str(self.mouvements.pop(0))]
        
        if self.objetVu is not None:
            if self.posCurseur == self.bestcandidat:
                self.repli = 'aucun'
            elif self.posCurseur[1] == self.bestcandidat[1]:
                self.repli = 'intensite'
            else:
                self.repli = 'voisine_' + str(abs(self.bestcandidat[0] - self.posCurseur[0]))

            self.casierChoisi = self.posCurseur
            return ["PRENDRE", self.objetVu]
        else:
            self.repli = 'armoire vide'
            return ["PRENDRE", ""]

def getPossibleObjects(armoire, emotion, intensite):
    intensiteIndex = intensites.index(intensite)
    emotionIndex = emotions.index(emotion)

    possibleObjects = {}
    candidats = MouvementDansArmoire.findCandidat(None, intensiteIndex, emotionIndex)
    objet = None
    repli = 'armoire vide'

    for i, e in candidats:

        objet = armoire['casiers'][i * 8 + e]['objet']

        if objet is not None:
            if (i, e) == (intensiteIndex, emotionIndex):
                repli = 'aucun'
            elif e == emotionIndex:
                repli = 'intensite'
            else:
                repli = 'voisine_' + str(abs(emotionIndex - e))

            possibleObjects[objet] = repli

    if possibleObjects == {}:
        possibleObjects[objet] = (repli, (i,e))

    return possibleObjects