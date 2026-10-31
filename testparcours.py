"""
Tests du projet "Robot de reconfort".

Lancement (depuis la racine du projet) :
    python3 -m unittest test_projet -v
ou, si pytest est installe :
    pytest test_projet.py -v

Contenu :
  1. reconfort_io      : lecture JSON, normaliser, Trace
  2. consultDico       : dictionnaire des emotions
  3. parcours          : BFS, direction, mouvement
  4. MouvementDansMap  : trajet vers un objectif
  5. MouvementDansArmoire : candidats, deplacements du curseur, objets possibles
  6. Explorer          : exploration d'une petite carte synthetique
  7. agentExemple      : fonction dist
  8. Integration       : main.py complet sur les vrais fichiers (ignore si absents)

Les tests marques @expectedFailure documentent des bugs connus : ils
passeront "en echec attendu" tant que le bug existe, et signaleront
"unexpected success" des qu'il sera corrige (retirer alors le decorateur).
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def setUpModule():
    # consultDico charge "donnees/dictionnaire.json" avec un chemin relatif
    os.chdir(ROOT)


def _importer_projet():
    """L'ordre compte : Environment d'abord, pour eviter les imports
    circulaires entre Environment, parcours et agentExemple."""
    import Environment  # noqa: F401
    import parcours
    import MouvementDansMap
    import MouvementDansArmoire
    import Explorer
    from src import agentExemple
    return parcours, MouvementDansMap, MouvementDansArmoire, Explorer, agentExemple


# ===========================================================================
# 1. reconfort_io
# ===========================================================================

import reconfort_io as rio


class TestNormaliser(unittest.TestCase):
    def test_exemple_enonce(self):
        self.assertEqual(rio.normaliser("Je suis TERRIFIEE, vraiment !"),
                         ["je", "suis", "terrifiee", "vraiment"])

    def test_accents_retires(self):
        self.assertEqual(rio.normaliser("Éléphant à l'été"),
                         ["elephant", "a", "l", "ete"])

    def test_ponctuation_et_chiffres_separent(self):
        self.assertEqual(rio.normaliser("a1b--c"), ["a", "b", "c"])

    def test_vide(self):
        self.assertEqual(rio.normaliser(""), [])
        self.assertEqual(rio.normaliser("  !?  "), [])


class TestLectureJson(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _ecrire(self, nom, contenu):
        p = self.dir / nom
        p.write_text(contenu, encoding="utf-8")
        return p

    def test_fichier_valide(self):
        p = self._ecrire("c.json", json.dumps(
            {"format": "robot-reconfort/carte", "version": 1}))
        self.assertEqual(rio.charger_carte(p)["version"], 1)

    def test_fichier_absent(self):
        with self.assertRaises(rio.ErreurFichier):
            rio.charger_carte(self.dir / "absent.json")

    def test_json_invalide(self):
        p = self._ecrire("x.json", "{pas du json")
        with self.assertRaises(rio.ErreurFichier):
            rio.charger_carte(p)

    def test_racine_pas_un_objet(self):
        p = self._ecrire("x.json", "[1, 2]")
        with self.assertRaises(rio.ErreurFichier):
            rio.charger_carte(p)

    def test_mauvais_format(self):
        p = self._ecrire("x.json", json.dumps(
            {"format": "robot-reconfort/armoire", "version": 1}))
        with self.assertRaises(rio.ErreurFichier):
            rio.charger_carte(p)

    def test_mauvaise_version(self):
        p = self._ecrire("x.json", json.dumps(
            {"format": "robot-reconfort/carte", "version": 99}))
        with self.assertRaises(rio.ErreurFichier):
            rio.charger_carte(p)

    def test_non_utf8(self):
        p = self.dir / "x.json"
        p.write_bytes(b'{"a": "\xff\xfe"}')
        with self.assertRaises(rio.ErreurFichier):
            rio.charger_carte(p)

    def test_chaque_chargeur_verifie_son_format(self):
        for nom, charger in [("carte", rio.charger_carte),
                             ("dictionnaire", rio.charger_dictionnaire),
                             ("armoire", rio.charger_armoire),
                             ("scenario", rio.charger_scenario),
                             ("trace", rio.charger_trace)]:
            p = self._ecrire(f"{nom}.json", json.dumps(
                {"format": f"robot-reconfort/{nom}", "version": 1}))
            self.assertEqual(charger(p)["format"], f"robot-reconfort/{nom}")


class TestTrace(unittest.TestCase):
    def setUp(self):
        self.trace = rio.Trace("carte_test", "scenario_test", ["A", "B"])

    def _pas(self, **kw):
        args = dict(demande=1, position=(1, 1), casier=(0, 0),
                    action="ATTENDRE")
        args.update(kw)
        self.trace.ajouter_pas(**args)

    def test_pas_numerotes(self):
        self._pas()
        self._pas(action="AVANCER", argument="N")
        self.assertEqual([p["t"] for p in self.trace.pas], [0, 1])

    def test_action_inconnue(self):
        with self.assertRaises(ValueError):
            self._pas(action="DANSER")

    def test_avancer_sans_direction(self):
        with self.assertRaises(ValueError):
            self._pas(action="AVANCER", argument=None)
        with self.assertRaises(ValueError):
            self._pas(action="CHERCHER", argument="X")

    def test_livraison_repli_invalide(self):
        with self.assertRaises(ValueError):
            self.trace.ajouter_livraison(1, "R1", "joie", "faible", (0, 0),
                                         "n_importe_quoi", "x", True)

    def test_echec_sans_motif(self):
        with self.assertRaises(ValueError):
            self.trace.ajouter_livraison(1, "R1", None, None, None,
                                         "aucun", None, False)

    def test_resume_et_pas_utilises(self):
        self._pas(demande=1)
        self._pas(demande=1)
        self._pas(demande=2)
        self.trace.ajouter_livraison(1, "R1", "joie", "faible", (0, 0),
                                     "aucun", "x", True)
        self.trace.ajouter_livraison(2, "R2", None, None, None, "aucun",
                                     None, False, "armoire vide")
        d = self.trace.en_dictionnaire()
        self.assertEqual(d["livraisons"][0]["pas_utilises"], 2)
        self.assertEqual(d["livraisons"][1]["pas_utilises"], 1)
        self.assertEqual(d["resume"], {"demandes": 2, "reussies": 1,
                                       "echecs": 1, "pas_total": 3})

    def test_ecriture_et_relecture(self):
        self._pas()
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "sous" / "dossier" / "trace.json"
            self.trace.ecrire(chemin)
            relu = rio.charger_trace(chemin)
        self.assertEqual(relu["carte"], "carte_test")
        self.assertEqual(relu["equipe"], ["A", "B"])
        self.assertEqual(len(relu["pas"]), 1)


# ===========================================================================
# 2. consultDico
# ===========================================================================

EMOTIONS = ["joie", "confiance", "peur", "surprise",
            "tristesse", "degout", "colere", "anticipation"]
INTENSITES = ["faible", "moyenne", "forte"]

DICO_PATH = ROOT / "donnees" / "dictionnaire.json"


@unittest.skipUnless(DICO_PATH.exists(), "donnees/dictionnaire.json absent")
class TestConsultDico(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import consultDico
        cls.cd = consultDico

    def test_normaliser_identique_a_rio(self):
        txt = "Je suis TERRIFIÉE, vraiment !"
        self.assertEqual(self.cd.normaliser(txt), rio.normaliser(txt))

    def test_toutes_les_formes_sont_reconnues(self):
        dico = rio.charger_dictionnaire(DICO_PATH)
        for ent in dico["entrees"]:
            self.assertIn(ent["emotion"], EMOTIONS)
            self.assertIn(ent["intensite"], INTENSITES)
            for forme in ent["formes"]:
                res = self.cd.findEmotionIntensite([forme])
                self.assertIsNotNone(res, f"forme non reconnue : {forme}")
                self.assertIn(res[1], EMOTIONS)
                self.assertIn(res[0], INTENSITES)

    def test_format_du_retour(self):
        dico = rio.charger_dictionnaire(DICO_PATH)
        ent = dico["entrees"][0]
        phrase = "Aujourd'hui je me sens " + ent["formes"][0] + " !"
        res = self.cd.EmotionInfoFromSentence(phrase)
        self.assertEqual(len(res), 2)          # [intensite, emotion]

    def test_message_sans_mot_connu(self):
        self.assertIsNone(self.cd.findEmotionIntensite(["zzzz", "qqqq"]))

    @unittest.expectedFailure
    def test_environment_gere_message_sans_emotion(self):
        """Bug connu : Environment fait `intensite, emotion = ...` et plante
        si aucun mot du message n'est dans le dictionnaire (retour None)."""
        r = self.cd.EmotionInfoFromSentence("zzzz qqqq")
        intensite, emotion = r  # TypeError tant que r vaut None


# ===========================================================================
# 3. parcours
# ===========================================================================

def _carte(lignes):
    return [list(l) for l in lignes]


class TestParcours(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parcours = _importer_projet()[0]

    def test_depart_egal_but(self):
        c = _carte(["###", "#.#", "###"])
        self.assertEqual(self.parcours.deplacement((1, 1), (1, 1), c),
                         [(1, 1)])

    def test_chemin_droit(self):
        c = _carte(["#####", "#...#", "#####"])
        self.assertEqual(self.parcours.deplacement((1, 1), (1, 3), c),
                         [(1, 1), (1, 2), (1, 3)])

    def test_contourne_un_mur(self):
        c = _carte(["#####",
                    "#.#.#",
                    "#...#",
                    "#####"])
        chemin = self.parcours.deplacement((1, 1), (1, 3), c)
        self.assertEqual(len(chemin), 5)       # 4 pas, 5 cases
        self.assertEqual(chemin[0], (1, 1))
        self.assertEqual(chemin[-1], (1, 3))
        for a, b in zip(chemin, chemin[1:]):
            self.assertEqual(abs(a[0] - b[0]) + abs(a[1] - b[1]), 1)
            self.assertEqual(c[b[0]][b[1]], ".")

    def test_but_inatteignable(self):
        c = _carte(["#####",
                    "#.#.#",
                    "#####"])
        self.assertEqual(self.parcours.deplacement((1, 1), (1, 3), c), [])

    def test_accepte_des_listes(self):
        c = _carte(["#####", "#...#", "#####"])
        self.assertEqual(self.parcours.deplacement([1, 1], [1, 2], c),
                         [(1, 1), (1, 2)])

    def test_direction(self):
        d = self.parcours.direction
        self.assertEqual(d((2, 2), (1, 2)), ["AVANCER", "N"])
        self.assertEqual(d((2, 2), (3, 2)), ["AVANCER", "S"])
        self.assertEqual(d((2, 2), (2, 1)), ["AVANCER", "O"])
        self.assertEqual(d((2, 2), (2, 3)), ["AVANCER", "E"])

    def test_mouvement(self):
        chemin = [(1, 1), (1, 2), (2, 2)]
        self.assertEqual(self.parcours.mouvement(chemin),
                         [["AVANCER", "E"], ["AVANCER", "S"]])
        self.assertEqual(self.parcours.mouvement([(1, 1)]), [])


# ===========================================================================
# 4. MouvementDansMap
# ===========================================================================

class TestMouvementDansMap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.mdm, _, _, _ = _importer_projet()

    def test_trajet_vers_case_voisine_de_l_objectif(self):
        # 'A' (armoire) en (1,4) : le robot doit s'arreter en (1,3)
        c = _carte(["######",
                    "#...A#",
                    "######"])
        m = self.mdm.MouvementDansMap(None, (1, 1), (1, 4), c)
        self.assertEqual(m.nextAction(), ["AVANCER", "E"])
        self.assertEqual(m.nextAction(), ["AVANCER", "E"])
        self.assertEqual(m.nextAction(), ["ATTENDRE", ""])

    def test_deja_a_cote(self):
        c = _carte(["######",
                    "#..A.#",
                    "######"])
        m = self.mdm.MouvementDansMap(None, (1, 2), (1, 3), c)
        self.assertEqual(m.nextAction(), ["ATTENDRE", ""])

    def test_choisit_le_voisin_le_plus_proche(self):
        c = _carte(["#######",
                    "#.....#",
                    "#..A..#",
                    "#.....#",
                    "#######"])
        chemin = self.mdm.bestPathAmongNeighbor((1, 1), (2, 3), c)
        self.assertEqual(chemin[-1] in [(1, 3), (2, 2), (3, 3), (2, 4)], True)
        self.assertEqual(len(chemin), 3)       # 2 pas


# ===========================================================================
# 5. MouvementDansArmoire
# ===========================================================================

class TestMouvementDansArmoire(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, _, cls.mda, _, _ = _importer_projet()

    def test_constantes(self):
        self.assertEqual(self.mda.emotions, EMOTIONS)
        self.assertEqual(self.mda.intensites, INTENSITES)

    def test_candidats_nombre_et_ordre(self):
        cands = self.mda.MouvementDansArmoire.findCandidat(None, 1, 0)
        self.assertEqual(len(cands), 15)
        self.assertEqual(cands[:3], [[1, 0], [0, 0], [2, 0]])
        # distance 1 : horaire puis anti-horaire (1 puis 7), intensite d'abord
        self.assertEqual(cands[3:5], [[1, 1], [1, 7]])
        # aucun doublon
        self.assertEqual(len({tuple(c) for c in cands}), 15)

    def test_candidats_intensite_forte(self):
        cands = self.mda.MouvementDansArmoire.findCandidat(None, 2, 3)
        self.assertEqual(cands[:3], [[2, 3], [1, 3], [0, 3]])

    def test_deplacement_nul(self):
        m = self.mda.MouvementDansArmoire(None, (1, 0), "joie", "moyenne")
        self.assertEqual(m.bestcandidat, [1, 0])
        self.assertEqual(m.mouvements, [])
        self.assertEqual(len(m.candidats), 14)

    def test_deplacement_vertical_puis_horizontal(self):
        m = self.mda.MouvementDansArmoire(None, (0, 0), "peur", "forte")
        self.assertEqual(m.bestcandidat, [2, 2])
        self.assertEqual(m.mouvements, ["S", "S", "E", "E"])

    def test_deplacement_horizontal_circulaire(self):
        f = self.mda.MouvementDansArmoire.deplacerDansArmoire
        self.assertEqual(f(None, (1, 0), (1, 7)), ["O"])        # via le bord
        self.assertEqual(f(None, (1, 7), (1, 0)), ["E"])
        self.assertEqual(f(None, (1, 0), (1, 3)), ["E", "E", "E"])
        self.assertEqual(f(None, (1, 0), (1, 5)), ["O", "O", "O"])
        self.assertEqual(f(None, (2, 3), (0, 3)), ["N", "N"])

    def _armoire(self, contenu):
        """contenu : {(ligne, colonne): objet}"""
        casiers = [{"ligne": i, "colonne": e, "emotion": EMOTIONS[e],
                    "intensite": INTENSITES[i], "objet": None}
                   for i in range(3) for e in range(8)]
        for (i, e), obj in contenu.items():
            casiers[i * 8 + e]["objet"] = obj
        return {"casiers": casiers}

    def test_objets_possibles_exact(self):
        arm = self._armoire({(1, 0): "photo"})
        self.assertEqual(self.mda.getPossibleObjects(arm, "joie", "moyenne"),
                         {"photo": "aucun"})

    def test_objets_possibles_repli_intensite(self):
        arm = self._armoire({(2, 0): "peluche"})
        self.assertEqual(self.mda.getPossibleObjects(arm, "joie", "moyenne"),
                         {"peluche": "intensite"})

    def test_objets_possibles_repli_voisine(self):
        arm = self._armoire({(1, 1): "the"})
        self.assertEqual(self.mda.getPossibleObjects(arm, "joie", "moyenne"),
                         {"the": "voisine_1"})

    def test_objets_possibles_plusieurs(self):
        arm = self._armoire({(1, 0): "photo", (0, 0): "livre", (1, 2): "plaid"})
        res = self.mda.getPossibleObjects(arm, "joie", "moyenne")
        self.assertEqual(res["photo"], "aucun")
        self.assertEqual(res["livre"], "intensite")
        self.assertEqual(res["plaid"], "voisine_2")

    def test_armoire_vide(self):
        res = self.mda.getPossibleObjects(self._armoire({}), "joie", "faible")
        self.assertNotIn("photo", res)
        self.assertEqual(len(res), 1)          # seule la cle None (armoire vide)

    @unittest.expectedFailure
    def test_voisine_circulaire(self):
        """Bug connu : joie(0) et anticipation(7) sont voisines (distance 1
        sur le cercle) mais le repli calcule abs(0 - 7) = 7."""
        arm = self._armoire({(1, 7): "bougie"})
        res = self.mda.getPossibleObjects(arm, "joie", "moyenne")
        self.assertEqual(res, {"bougie": "voisine_1"})

    def test_updatestate_et_nextaction_trouve_objet(self):
        """Simule l'armoire avec un faux agent : curseur deja sur le bon casier."""
        class FauxAgent:
            newinfo = {"contenu_casier": {"objet": "photo"},
                       "posCasier": [1, 0]}
        m = self.mda.MouvementDansArmoire(FauxAgent(), (1, 0), "joie", "moyenne")
        m.updateState()
        self.assertEqual(m.nextAction(), ["PRENDRE", "photo"])
        self.assertEqual(m.repli, "aucun")

    def test_nextaction_cherche_d_abord(self):
        class FauxAgent:
            newinfo = {"contenu_casier": {"objet": None}, "posCasier": [1, 0]}
        m = self.mda.MouvementDansArmoire(FauxAgent(), (1, 0), "joie", "forte")
        # best candidat [2,0] -> un mouvement S a faire
        self.assertEqual(m.nextAction(), ["CHERCHER", "S"])


# ===========================================================================
# 6. Explorer (carte synthetique)
# ===========================================================================

VERITE = [
    "#######",
    "#..#..#",
    "#..#..#",
    "#.....#",
    "#######",
]


class FauxAgentExplorer:
    def __init__(self):
        self.newinfo = {}


def _perception(grille, pos):
    x, y = pos
    return {"N": grille[x - 1][y], "S": grille[x + 1][y],
            "E": grille[x][y + 1], "O": grille[x][y - 1]}


class TestExplorer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.Explorer = _importer_projet()[3].Explorer

    def _explorer(self, verite, depart, max_pas=300):
        h, w = len(verite), len(verite[0])
        agent = FauxAgentExplorer()
        ex = self.Explorer(agent, {"hauteur": h, "largeur": w})
        pos = list(depart)
        pas = 0
        while pas < max_pas:
            agent.newinfo = {"posTerrain": list(pos),
                             "perception": _perception(verite, pos)}
            ex.updateState()
            action = ex.nextAction()
            if ex.is_finish:
                break
            self.assertEqual(action[0], "AVANCER")
            dx, dy = {"N": (-1, 0), "S": (1, 0),
                      "O": (0, -1), "E": (0, 1)}[action[1]]
            nx, ny = pos[0] + dx, pos[1] + dy
            self.assertEqual(verite[nx][ny], ".", "l'explorateur fonce dans un mur")
            pos = [nx, ny]
            pas += 1
        return ex, pas

    def test_carte_initiale_bordures(self):
        ex = self.Explorer(FauxAgentExplorer(), {"hauteur": 4, "largeur": 5})
        self.assertEqual(ex.carte_mental[0], ["#"] * 5)
        self.assertEqual(ex.carte_mental[3], ["#"] * 5)
        self.assertEqual(ex.carte_mental[1], ["#", "?", "?", "?", "#"])

    def test_exploration_complete(self):
        ex, pas = self._explorer(VERITE, (1, 1))
        self.assertTrue(ex.is_finish, "l'exploration ne se termine pas")
        for x, ligne in enumerate(VERITE):
            for y, c in enumerate(ligne):
                if c == ".":
                    self.assertEqual(ex.carte_mental[x][y], ".",
                                     f"case libre ({x},{y}) non decouverte")
        self.assertLess(pas, 60)

    def test_exploration_depart_ailleurs(self):
        ex, _ = self._explorer(VERITE, (3, 5))
        self.assertTrue(ex.is_finish)
        self.assertEqual(ex.carte_mental[1][1], ".")

    def test_murs_decouverts(self):
        ex, _ = self._explorer(VERITE, (1, 1))
        self.assertEqual(ex.carte_mental[1][3], "#")
        self.assertEqual(ex.carte_mental[2][3], "#")

    def test_piece_unique_une_case(self):
        v = ["###", "#.#", "###"]
        ex, pas = self._explorer(v, (1, 1))
        self.assertTrue(ex.is_finish)
        self.assertEqual(pas, 0)

    def test_zone_inaccessible_ignoree(self):
        v = ["#######",
             "#.#...#",
             "#######"]
        ex, _ = self._explorer(v, (1, 1))
        self.assertTrue(ex.is_finish)


# ===========================================================================
# 7. agentExemple
# ===========================================================================

class TestAgentExemple(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ae = _importer_projet()[4]

    def test_dist_manhattan(self):
        self.assertEqual(self.ae.dist((0, 0), (0, 0)), 0)
        self.assertEqual(self.ae.dist((1, 1), (1, 2)), 1)
        self.assertEqual(self.ae.dist((1, 1), (4, 5)), 7)
        self.assertEqual(self.ae.dist([4, 5], [1, 1]), 7)


# ===========================================================================
# 8. Integration : main.py sur les vrais fichiers
# ===========================================================================

CARTE = ROOT / "cartes" / "appartement_01.json"
SCENARIO = ROOT / "scenarios" / "scenario_01.json"
DONNEES = ROOT / "donnees"


@unittest.skipUnless(CARTE.exists() and SCENARIO.exists() and DICO_PATH.exists(),
                     "fichiers carte/scenario/donnees absents")
class TestIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.sortie = Path(cls.tmp.name) / "trace_test.json"
        cls.proc = subprocess.run(
            [sys.executable, "main.py", str(CARTE), str(SCENARIO),
             str(DONNEES), str(cls.sortie)],
            cwd=ROOT, capture_output=True, text=True, timeout=300)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_code_retour_zero(self):
        self.assertEqual(self.proc.returncode, 0, self.proc.stderr[-2000:])

    def test_trace_ecrite_et_valide(self):
        self.assertTrue(self.sortie.exists(), "aucune trace produite")
        t = rio.charger_trace(self.sortie)
        for cle in ("carte", "scenario", "equipe", "pas", "livraisons", "resume"):
            self.assertIn(cle, t)
        self.assertEqual(t["resume"]["pas_total"], len(t["pas"]))
        self.assertEqual(t["resume"]["demandes"], len(t["livraisons"]))
        self.assertEqual(t["resume"]["reussies"] + t["resume"]["echecs"],
                         len(t["livraisons"]))

    def test_pas_coherents(self):
        t = rio.charger_trace(self.sortie)
        self.assertEqual([p["t"] for p in t["pas"]], list(range(len(t["pas"]))))
        for p in t["pas"]:
            self.assertIn(p["action"], rio.ACTIONS)
            self.assertEqual(len(p["position"]), 2)
            self.assertEqual(len(p["casier"]), 2)
            self.assertTrue(0 <= p["casier"][0] < 3)
            self.assertTrue(0 <= p["casier"][1] < 8)

    def test_deplacements_d_une_case(self):
        """Entre deux pas consecutifs, la position change d'au plus une case."""
        t = rio.charger_trace(self.sortie)
        for a, b in zip(t["pas"], t["pas"][1:]):
            d = abs(a["position"][0] - b["position"][0]) + \
                abs(a["position"][1] - b["position"][1])
            self.assertLessEqual(d, 1)

    def test_livraisons_coherentes(self):
        t = rio.charger_trace(self.sortie)
        scenario = rio.charger_scenario(SCENARIO)
        numeros = {d["numero"] for d in scenario["demandes"]}
        for l in t["livraisons"]:
            self.assertIn(l["demande"], numeros)
            self.assertIn(l["repli"], rio.REPLIS)
            if l["succes"]:
                self.assertIsNotNone(l["objet"])
            else:
                self.assertTrue(l["motif_echec"])

    def test_mauvais_nombre_d_arguments(self):
        r = subprocess.run([sys.executable, "main.py"], cwd=ROOT,
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 2)

    def test_carte_inexistante(self):
        r = subprocess.run(
            [sys.executable, "main.py", "nexistepas.json", str(SCENARIO),
             str(DONNEES), str(self.sortie)],
            cwd=ROOT, capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 1)
        self.assertIn("introuvable", r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)