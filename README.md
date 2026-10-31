# Robot de réconfort — Fauron & Lamkaddem & Thomas

Projet de semestre, master informatique (HAI716). Un robot à perception locale
consulte un dictionnaire, fouille une armoire et rapporte un objet à un
résident.

Langage : Python — Version : 3.10 ou plus

## Lancer

```
python3 -m main cartes/appartement_01.json scenarios/scenario_01.json donnees sorties/trace_GroupeFLT.json
```

### Visualiser la trace

```
python3 affichage.py sorties/trace_GroupeFLT.json
```

Si besoin : `chmod +x affichage.py`

### Dépendances

Aucune bibliothèque externe. L'affichage utilise `tkinter`:

```
sudo apt install python3-tk
```

## Tester

```
python3 -m unittest discover -s test -v
```

Les tests de `test/test.py` couvrent :

- la planification : le parcours en largeur (`deplacement`) sur de petites grilles écrites à la main (chemin de longueur connue, mur à contourner, même case, destination inaccessible) ;
- la conversion d'un chemin en directions (`direction`) ;
- l'exploration : le robot explore une petite carte complète à partir d'une perception locale uniquement ;
- la lecture du dictionnaire : mots reconnus, premier mot reconnu qui gagne, message sans mot connu ;
- le déplacement du sélecteur dans l'armoire, y compris le bouclage entre la colonne 7 et la colonne 0 dans les deux sens, et le choix du sens le plus court.

`testparcours.py` (à la racine) contient une suite plus large (lecture des
fichiers, `MouvementDansMap`, tests d'intégration sur `main.py`). Elle se lance
avec `python3 -m unittest testparcours -v`. Voir la section « Ce qui ne marche pas »
pour son état actuel.

## Organisation du code

| Fichier | Rôle |
|---|---|
| `main.py` | Point d'entrée : lit les 4 fichiers via `reconfort_io`, crée l'`Environment`, lance `env.run()`, écrit la trace. |
| `reconfort_io.py` | Fourni : lecture des fichiers JSON et écriture de la trace. |
| `src/Environment.py` | Chef d'orchestre et simulateur. Stocke les données (carte, armoire, dictionnaire, scénario), crée le `Robot`, définit les règles physiques du monde. À chaque pas : fournit sa perception à l'agent, récupère son action, l'exécute (`AVANCER`, `CONSULTER`, `CHERCHER`, `PRENDRE`, `DONNER`, `ATTENDRE`) et la journalise dans la trace. Calcule aussi les objets acceptables pour chaque demande. |
| `src/Robot.py` | L'agent. Machine à états `EXPLORER` → `DICTIONNAIRE` → `ARMOIRE` → `LIVRAISON` (puis retour à `DICTIONNAIRE` pour la demande suivante). Il choisit à chaque tour l'action à renvoyer et délègue le « comment » aux `ActionMaker`. |
| `src/ActionMaker/Explorer.py` | Construit toute la carte mentale à partir des 4 cases perçues et choisit la prochaine case à explorer (parcours en largeur). |
| `src/ActionMaker/MouvementDansMap.py` | Calcule le trajet et fournie l'action qui se rapproche des coordonées fournie, souvent un objectif (armoire, dictionnaire ou résident), avec la carte mentale. |
| `src/ActionMaker/MouvementDansArmoire.py` | liste ordonnée des casiers candidats et produit la suite de `CHERCHER` pour déplacer le sélecteur, avec bouclage des colonnes et ligne. |
| `src/parcours.py` | Parcours en largeur écrit à la main (file `deque` suggerée), `direction` et `mouvement` pour transformer un chemin en actions. |
| `src/consultDico.py` | Normalisation des messages (minuscules, sans accents, découpage sur les non-lettres) et recherche du premier mot reconnu dans le dictionnaire (section 6.1). |
| `affichage.py` | Visionneuse `tkinter` qui rejoue une trace pas à pas. |
| `test/test.py`, `testparcours.py` | Tests automatisés (voir ci-dessus). |
| `cartes/`, `scenarios/`, `donnees/` | Entrées : appartements, scénarios, dictionnaire et armoires. |
| `sorties/` | Traces générées. |
| `rendu.json` | Pour la correction. |

### Séparation perception / mémoire / décision / action

- **Perception** : `Environment.get_perception` renvoie au robot un packets d'informations qu'il a le droit de lire. sa position, les 4 cases adjacentes, la position du sélecteur, le contenu du casier courant et le résultat de sa lecture. Le robot ne lit jamais la grille du fichier de carte.
- **Mémoire** : L'environment stock la totalité des informations hors reflexion, l'agent les redemande à chaque tours pour mettre à jour son état et proposer sa prochaine action, les informations  de reflexion seulement comme la carte mentale sont stockées et partagées avec les objets ActionMakers .
- **Décision** : `Robot.UpdateState`/`Robot.nextState` / `Robot.compute_NextMove`, le robot calcule son état selon les nouvelles informations du tours puis selon son état, le robot choisis une action.
- **Action** : les `ActionMaker` produisent les actions des agents, ensuite elles sont récupérées par l'Environment`Environment.get_agentsActions` , puis `Environment._handleAction` l'exécute et l'écrit dans la trace.

## État

**Ce qui marche.**

- boucle de simulation complete et écriture de la trace.
- Exploration complète d'une carte grace à perception locale, avec carte mentale séparée de la carte réelle.
- Planification des actions pour réalisé le plus court chemin (parcours en largeur écrit à la main) vers la cible.
- Lecture du dictionnaire.
- Déplacement du sélecteur dans l'armoire avec bouclage des lignes et colonnes,calcul de l'ordre des casiers candidats selon la roue de Plutchik.
- Détection d'un résident inaccessible sans interrompre le scénario.
- Sur les cartes  et scénarios fournies, Tout les résultats sont ceux attendues mais rarement ne se sont pas déroulé comme prévue(voir ci dessous) .

**Ce qui ne marche pas/ ne va pas**

**Ce qui ne marche pas.**

- **Résident non livré au scénario 05.** Ce problème a été trouvé 5 heures avant le rendu. La demande 2 échoue : le casier visé a déjà été vidé par la demande 1, et le robot repart livrer sans objet. Cause probable : il y a un problème non identifier dans notre code Concernant l'état de l'agent `Chercher`, possiblement l'ActionMaker. Dans tout les cas, cette erreur n'est pas reconnu par l'agent.
- **non conformité à l'énoncé.** Nous avons pris des initiatives qui ne suivent pas exactement l'énoncé mais produise des résultats équivalent qu ce qui est atendue, par exemple perception qui donne à chaque pas plus d'information que se que demande l'énoncé. ce choix s'explique par la volonté de séparé la partie refléxion et le 'corp' de l'agent.
- **Pas de replanification réelle.** Le robot explore toute la carte avant de livrer, puis planifie une fois sur une carte complète. Il ne découvre jamais de mur en cours de route, ce qui coûte des pas.

## Vidéo

`demo.mp4` (ou le lien), également déclarée dans `rendu.json`.

*Le fichier vidéo n'est pas encore dans l'archive. Ajoutez-le, ou remplacez par l'URL, et gardez `rendu.json` cohérent.*
