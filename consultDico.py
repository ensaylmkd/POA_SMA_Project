import sys
from typing import Any, Dict, List, Optional, Sequence
import unicodedata
from pathlib import Path

# ---------------------------------------------------------------------------
# Normalisation des messages
# ---------------------------------------------------------------------------

def normaliser(texte: str) -> List[str]:
    """Decoupe un message en mots comparables au dictionnaire.

    Minuscules, accents retires, decoupage sur tout ce qui n'est pas une
    lettre. C'est exactement la regle de l'enonce, section 6.1 ;
    reimplementez-la vous-meme si vous travaillez dans un autre langage.

        >>> normaliser("Je suis TERRIFIEE, vraiment !")
        ['je', 'suis', 'terrifiee', 'vraiment']
    """
    decompose = unicodedata.normalize("NFD", texte.lower())
    sans_accents = "".join(
        c for c in decompose if unicodedata.category(c) != "Mn"
    )
    mots: List[str] = []
    courant: List[str] = []
    for caractere in sans_accents:
        if caractere.isalpha():
            courant.append(caractere)
        elif courant:
            mots.append("".join(courant))
            courant = []
    if courant:
        mots.append("".join(courant))
    return mots

def findEmotionIntensite(messageNorm):
    for elt in messageNorm:
        for ent in dico['entrees']:
            if elt in ent['formes']:
                return elt, ent['intensite'], ent['emotion']


#######################################################
######################   MAIN   #######################
#######################################################

## test ## 
import reconfort_io as rio
dico = rio.charger_dictionnaire("donnees/dictionnaire.json")

def main(argv):
    if len(argv) != 2:
        print(__doc__.strip())
        return 2

    print(argv[1])
    chemin_scenario = Path(argv[1])
    
    try:
        scenario = rio.charger_scenario(chemin_scenario)
    except rio.ErreurFichier as err:
        print(f"erreur de chargement : {err}", file=sys.stderr)
        return 1

    eilist = []
    for d in scenario["demandes"]:
        messageNorm = normaliser(d['message'])
        mot, intensite, emotion = findEmotionIntensite(messageNorm)
        print(mot, ' :', intensite, emotion)

    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))