import sys

def deplacerDansArmoire(posDepart, posArrivee):
    l, c = posDepart
    l2, c2 = posArrivee

    listDeplacements = []

    nbMouvVert = abs(l2 - l)
    for i in range(nbMouvVert):
        if l2 > l:
            listDeplacements.append('S')
        else:
            listDeplacements.append('N')

    a = (c2-c) % 8
    if a <= 8-a:
        for i in range(a):
            listDeplacements.append('E')
    else:
        for i in range(8-a):
            listDeplacements.append('O')

    return listDeplacements

def findCandidat(intensiteVoulue, emotionVoulue):
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

def findBestObjet(intensiteVoulue,emotionVoulue,posDepart):
    mouvements = []
    candidats = findCandidat(intensiteVoulue, emotionVoulue)
    objet = None
    posCurseur = posDepart
    repli = 'armoire vide'

    for i, e in candidats:
        mouvements.append(deplacerDansArmoire(posCurseur, [i, e]))
        posCurseur = [i, e]

        objet = armoire['casiers'][i * 8 + e]['objet']

        if objet is not None:
            if (i, e) == (intensiteVoulue, emotionVoulue):
                repli = 'aucun'
            elif e == emotionVoulue:
                repli = 'intensite'
            else:
                repli = 'voisine_' + str(abs(emotionVoulue - e))

            casierChoisi = [i, e]
            break

    print("Candidats :", candidats)
    print("Mouvements :", mouvements)

    return objet, casierChoisi, repli

#######################################################
######################   MAIN   #######################
#######################################################

## test ## 
import reconfort_io as rio
armoire = rio.charger_armoire("donnees/armoire_standard.json")

def main(argv):
    if len(argv) != 4:
        print(__doc__.strip())
        return 2
    posDepart = [int(v) for v in argv[1].split(",")]
    intensite = argv[2]
    emotion = argv[3]

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

    intensiteVoulue = intensites.index(intensite)
    emotionVoulue = emotions.index(emotion)

    objet, casierChoisi, repli = findBestObjet(intensiteVoulue, emotionVoulue, posDepart)

    if objet is not None:
        print("Casier choisi :", casierChoisi)
        print("Objet :", objet)
        print("Repli :", repli)
    else:
        print("Échec : armoire vide")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))