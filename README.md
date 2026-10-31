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
| `src/ActionMaker/Explorer.py` | Construit la carte mentale (bord = mur, reste = `?`) à partir des 4 cases perçues et choisit la prochaine case à explorer (la plus proche d'après un parcours en largeur). |
| `src/ActionMaker/MouvementDansMap.py` | Calcule le trajet vers une case libre adjacente à un objectif (armoire, dictionnaire ou résident) sur la carte mentale. |
| `src/ActionMaker/MouvementDansArmoire.py` | Règle de la section 6.2 : liste ordonnée des casiers candidats (distance sur la roue, écart d'intensité, intensité faible d'abord, sens horaire d'abord) et suite de `CHERCHER` pour déplacer le sélecteur, avec bouclage des colonnes. |
| `src/ActionMaker/IActionMaker.py` | Interface commune aux `ActionMaker` (`updateState`, `nextAction`). |
| `src/parcours.py` | Parcours en largeur écrit à la main (file `deque`), `direction` et `mouvement` pour transformer un chemin en actions. Pas de bibliothèque de plus court chemin. |
| `src/consultDico.py` | Normalisation des messages (minuscules, sans accents, découpage sur les non-lettres) et recherche du premier mot reconnu dans le dictionnaire (section 6.1). |
| `affichage.py` | Visionneuse `tkinter` qui rejoue une trace pas à pas. |
| `test/test.py`, `testparcours.py` | Tests automatisés (voir ci-dessus). |
| `cartes/`, `scenarios/`, `donnees/` | Entrées : appartements, scénarios, dictionnaire et armoires. |
| `sorties/` | Traces générées. |
| `rendu.json` | Contrat d'appel déclaré pour la correction. |

### Séparation perception / mémoire / décision / action

- **Perception** : `Environment.get_perception` renvoie au robot les 4 cases adjacentes, la position du sélecteur et le contenu du casier courant. Le robot ne lit jamais la grille du fichier de carte.
- **Mémoire** : la carte mentale (`Explorer.carte_mental`), partagée avec le `Robot`.
- **Décision** : `Robot.nextState` / `Robot.compute_NextMove` (choix de l'état et de l'action).
- **Action** : les `ActionMaker` produisent l'action, `Environment._handleAction` l'exécute et l'écrit dans la trace.

## État

**Ce qui marche.**

- Lecture des 4 fichiers, boucle de simulation et écriture de la trace au format `robot-reconfort/trace`.
- Exploration complète d'une carte à perception locale, avec carte mentale séparée de la carte réelle.
- Planification en plus court chemin (parcours en largeur écrit à la main) vers une case adjacente à la cible.
- Lecture du dictionnaire (premier mot reconnu) et calcul de l'ordre des casiers candidats selon la roue de Plutchik.
- Déplacement du sélecteur dans l'armoire avec bouclage des colonnes.
- Détection d'un résident muré (cas inaccessible) sans interrompre le scénario.
- Sur les cartes fournies, 4 scénarios sur 5 (hors `scenario_01`, voir plus bas) livrent la plupart des demandes ; `scenario_03` et `scenario_04` ont 6 livraisons réussies sur 6.

**Ce qui ne marche pas.**

- **Mauvais objet dans certains replis.** Sur `scenario_02` (1 échec sur 5) et `scenario_05` (1 échec sur 8), le robot livre un objet qui n'est pas dans la liste acceptable (`l'agent s'est trompé d'objet`). Cause probable : dans `MouvementDansArmoire`, le calcul de la distance de repli `voisine_N` utilise la ligne du casier (`[0]`, l'intensité) au lieu de la colonne (`[1]`, l'émotion), et la décision de s'arrêter sur un casier garni ne vérifie pas strictement l'ordre de priorité. À corriger.
- **Demandes suivantes qui échouent après un résident inaccessible.** Sur `scenario_01` (où `R1` est muré, ce qui est voulu), la demande 4 adressée à `R2`, pourtant accessible, échoue elle aussi avec « le résident n'est pas accessible ». La machine à états du `Robot` ne repart pas proprement après un échec. Cause exacte pas encore identifiée.
- **Pas de replanification réelle.** Le robot explore d'abord toute la carte, puis planifie sur une carte mentale complète. Il ne découvre donc jamais de mur « en route » : il ne se cogne jamais et ne répare jamais son plan. C'est correct mais coûteux en pas (exploration complète avant la première livraison), et la démonstration vidéo ne peut pas montrer de changement d'itinéraire.
- **Motifs d'échec non conformes.** Les motifs écrits dans la trace sont des phrases libres (« Le résident n'est pas accessible », « l'agent s'est trompé d'objet ») et non les chaînes attendues par l'énoncé (`resident inaccessible`, `armoire vide`, `emotion indeterminee`). Une demande dont aucun mot n'est reconnu n'est pas traitée explicitement avec `emotion indeterminee`.
- **Cas « armoire vide » mal géré.** Si les 15 casiers sont vides, le robot envoie `PRENDRE` avec un objet vide au lieu de déclarer l'échec proprement.
- **Validation des fichiers (section 5.6) non faite.** Seules les vérifications minimales de `reconfort_io.py` sont actives (en-tête `format` / `version`). Grille non rectangulaire, positions incohérentes, doublons, casiers hors armoire, etc. ne sont pas détectés : il n'y a donc pas de code de retour non nul ni de message d'erreur pour ces cas.
- **Chemin codé en dur.** `src/consultDico.py` charge `donnees/dictionnaire.json` à l'import avec un chemin relatif : le programme ne fonctionne que lancé depuis la racine du projet, et ignore le dossier de données passé en argument.
- **Tests incomplets.** `test/test.py` ne couvre pas la replanification, la règle de repli complète (casier vide, colonne entière vide, aucun casier garni à distance ≤ 2), la validation des fichiers ni le résident muré sur une grille minuscule. Il importe aussi `affichage` (donc `tkinter`) alors que les tests n'en ont pas besoin. `testparcours.py` échoue à l'import de certains modules (`MouvementDansMap` introuvable) : ses chemins d'import n'ont pas suivi la réorganisation en `src/`.
- **Sortie console très bavarde.** Chaque action affiche une ligne (`[avancerAgent]Succes: ...`), ce qui noie les messages d'erreur utiles.

## Vidéo

`demo.mp4` (ou le lien), également déclarée dans `rendu.json`.

*Le fichier vidéo n'est pas encore dans l'archive. Ajoutez-le, ou remplacez par l'URL, et gardez `rendu.json` cohérent.*
