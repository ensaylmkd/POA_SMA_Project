#!/usr/bin/env python3

import sys
from pathlib import Path
import time 

import reconfort_io as rio

def initMap(mapCharged):
    width=len(mapCharged[0])
    height=len(mapCharged)

    map = [['#' for _ in range(width)] for _ in range(height)]

    for r in range(1, height - 1):
        for c in range(1, width - 1):
            map[r][c] = ' '
    
    return map

def updateMap(position, perception, map):
    height = len(map)
    width = len(map[0])

    r, c = position

    if r > 0 and (map[r - 1][c] == ' ' or map[r - 1][c] == 'R'):
        map[r - 1][c] = perception['N']

    if r < height - 1 and (map[r + 1][c] == ' ' or map[r + 1][c] == 'R'):
        map[r + 1][c] = perception['S']

    if c < width - 1 and (map[r][c + 1] == ' ' or map[r][c + 1] == 'R'):
        map[r][c + 1] = perception['E']

    if c > 0 and (map[r][c - 1] == ' ' or map[r][c - 1] == 'R'):
        map[r][c - 1] = perception['O']

    map[r][c] = 'R'

    return map


def showMap(map):
    for r in range(len(map)):
        for c in range(len(map[0])):
            print(map[r][c], end='')
        print()

def main(argv):
    if len(argv) != 2:
        print(__doc__.strip())
        return 2

    chemin_trace = Path(argv[1])

    try:
        trace = rio.charger_trace(chemin_trace)
        carte = rio.charger_carte("cartes/"+trace["carte"]+".json")
    except rio.ErreurFichier as err:
        print(f"erreur de chargement : {err}", file=sys.stderr)
        return 1

    map = initMap(carte['grille'])
    showMap(map)

    for step in trace["pas"]:
        time.sleep(0.2)
        map = updateMap(step['position'], step['perception'], map)
        showMap(map)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
