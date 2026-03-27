# backend/tests/test_api_integration.py
"""
Tests d'intégration : Flask API → algorithmes → réponse JSON
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app as flask_app


@pytest.fixture
def client():
    flask_app.app.config['TESTING'] = True
    with flask_app.app.test_client() as c:
        yield c


# ── /api/compare ─────────────────────────────────────────────────────────────

class TestApiCompare:

    PLATS_BASE = [
        {"nom": "Plat A", "prep": 15, "cuisson": 17},
        {"nom": "Plat B", "prep": 11, "cuisson": 16},
        {"nom": "Plat C", "prep": 0,  "cuisson": 12},
    ]

    def test_compare_retourne_200(self, client):
        r = client.post('/api/compare', json={
            "plats": self.PLATS_BASE,
            "nb_commis": 1, "nb_fours": 1,
            "algos": ["johnson", "lpt", "fifo"]
        })
        assert r.status_code == 200

    def test_compare_structure_reponse(self, client):
        r = client.post('/api/compare', json={
            "plats": self.PLATS_BASE,
            "nb_commis": 1, "nb_fours": 1,
            "algos": ["johnson", "lpt"]
        })
        data = r.get_json()
        assert "resultats" in data
        assert "meilleur_algo" in data
        assert "meilleur_makespan" in data
        assert "est_optimal_garanti" in data

    def test_compare_johnson_optimal_1_commis_1_four(self, client):
        r = client.post('/api/compare', json={
            "plats": self.PLATS_BASE,
            "nb_commis": 1, "nb_fours": 1,
            "algos": ["johnson"]
        })
        data = r.get_json()
        assert data["est_optimal_garanti"] is True
        assert data["resultats"]["johnson"]["est_optimal"] is True

    def test_compare_makespan_positif(self, client):
        r = client.post('/api/compare', json={
            "plats": self.PLATS_BASE,
            "nb_commis": 1, "nb_fours": 1,
            "algos": ["johnson", "neh", "lpt", "fifo"]
        })
        data = r.get_json()
        for algo, res in data["resultats"].items():
            assert res["makespan"] > 0, f"{algo} makespan nul"

    def test_compare_johnson_meilleur_ou_egal(self, client):
        """Johnson doit être optimal ou égal au meilleur sur 1+1."""
        r = client.post('/api/compare', json={
            "plats": self.PLATS_BASE,
            "nb_commis": 1, "nb_fours": 1,
            "algos": ["johnson", "neh", "lpt", "fifo"]
        })
        data = r.get_json()
        ms_johnson = data["resultats"]["johnson"]["makespan"]
        ms_meilleur = data["meilleur_makespan"]
        assert ms_johnson == ms_meilleur

    def test_compare_ratio_meilleur_vaut_1(self, client):
        r = client.post('/api/compare', json={
            "plats": self.PLATS_BASE,
            "nb_commis": 1, "nb_fours": 1,
            "algos": ["johnson", "lpt"]
        })
        data = r.get_json()
        assert data["resultats"][data["meilleur_algo"]]["ratio"] == 1.0

    def test_compare_ordre_contient_tous_les_plats(self, client):
        r = client.post('/api/compare', json={
            "plats": self.PLATS_BASE,
            "nb_commis": 1, "nb_fours": 1,
            "algos": ["johnson"]
        })
        data = r.get_json()
        noms_attendus = {p["nom"] for p in self.PLATS_BASE}
        noms_retournes = set(data["resultats"]["johnson"]["ordre"])
        assert noms_retournes == noms_attendus

    def test_compare_erreur_sans_plats(self, client):
        r = client.post('/api/compare', json={
            "plats": [], "nb_commis": 1, "nb_fours": 1
        })
        assert r.status_code == 400

    def test_compare_erreur_trop_de_plats(self, client):
        plats = [{"nom": f"P{i}", "prep": 5, "cuisson": 5} for i in range(31)]
        r = client.post('/api/compare', json={
            "plats": plats, "nb_commis": 1, "nb_fours": 1
        })
        assert r.status_code == 400

    def test_compare_un_seul_plat(self, client):
        r = client.post('/api/compare', json={
            "plats": [{"nom": "Solo", "prep": 10, "cuisson": 5}],
            "nb_commis": 1, "nb_fours": 1,
            "algos": ["johnson", "lpt"]
        })
        assert r.status_code == 200
        data = r.get_json()
        assert data["meilleur_makespan"] > 0

    def test_compare_multi_commis_fours(self, client):
        plats = [{"nom": f"P{i}", "prep": i+1, "cuisson": 10-i} for i in range(6)]
        r = client.post('/api/compare', json={
            "plats": plats, "nb_commis": 2, "nb_fours": 2,
            "algos": ["johnson", "neh", "lpt"]
        })
        assert r.status_code == 200
        data = r.get_json()
        assert data["est_optimal_garanti"] is False  # pas 1+1


# ── /api/jouer ───────────────────────────────────────────────────────────────

class TestApiJouer:

    PLATS = [
        {"nom": "Plat A", "prep": 15, "cuisson": 17},
        {"nom": "Plat B", "prep": 11, "cuisson": 16},
        {"nom": "Plat C", "prep": 0,  "cuisson": 12},
    ]

    def test_jouer_retourne_200(self, client):
        r = client.post('/api/jouer', json={
            "plats": self.PLATS,
            "ordre_human": [0, 1, 2],
            "nb_commis": 1, "nb_fours": 1
        })
        assert r.status_code == 200

    def test_jouer_structure_reponse(self, client):
        r = client.post('/api/jouer', json={
            "plats": self.PLATS,
            "ordre_human": [0, 1, 2],
            "nb_commis": 1, "nb_fours": 1
        })
        data = r.get_json()
        assert "makespan_human" in data
        assert "makespan_johnson" in data
        assert "ordre_human" in data
        assert "ordre_johnson" in data

    def test_jouer_johnson_meilleur_ou_egal(self, client):
        """L'ordre humain ne peut pas battre Johnson."""
        r = client.post('/api/jouer', json={
            "plats": self.PLATS,
            "ordre_human": [2, 0, 1],
            "nb_commis": 1, "nb_fours": 1
        })
        data = r.get_json()
        assert data["makespan_johnson"] <= data["makespan_human"]

    def test_jouer_ordre_optimal_egal_johnson(self, client):
        """Si l'humain donne l'ordre Johnson, les makespans sont égaux."""
        # Trouver l'ordre Johnson d'abord via /api/compare
        rc = client.post('/api/compare', json={
            "plats": self.PLATS, "nb_commis": 1, "nb_fours": 1,
            "algos": ["johnson"]
        })
        ordre_johnson_noms = rc.get_json()["resultats"]["johnson"]["ordre"]
        noms = [p["nom"] for p in self.PLATS]
        ordre_idx = [noms.index(n) for n in ordre_johnson_noms]

        r = client.post('/api/jouer', json={
            "plats": self.PLATS,
            "ordre_human": ordre_idx,
            "nb_commis": 1, "nb_fours": 1
        })
        data = r.get_json()
        assert data["makespan_human"] == data["makespan_johnson"]

    def test_jouer_erreur_sans_plats(self, client):
        r = client.post('/api/jouer', json={
            "plats": [], "ordre_human": [], "nb_commis": 1, "nb_fours": 1
        })
        assert r.status_code == 400

    def test_jouer_erreur_indice_invalide(self, client):
        r = client.post('/api/jouer', json={
            "plats": self.PLATS,
            "ordre_human": [0, 1, 99],
            "nb_commis": 1, "nb_fours": 1
        })
        assert r.status_code == 400


# ── /api/instances ───────────────────────────────────────────────────────────

class TestApiInstances:

    def test_list_instances_retourne_200(self, client):
        r = client.get('/api/instances')
        assert r.status_code == 200

    def test_list_instances_structure(self, client):
        data = client.get('/api/instances').get_json()
        assert "instances" in data
        assert isinstance(data["instances"], list)
        assert len(data["instances"]) > 0

    def test_get_instance_connue(self, client):
        r = client.get('/api/instances/exemple_1_sujet')
        assert r.status_code == 200
        data = r.get_json()
        assert data["nom"] == "exemple_1_sujet"
        assert "plats" in data

    def test_get_instance_inconnue_retourne_404(self, client):
        r = client.get('/api/instances/nexiste_pas')
        assert r.status_code == 404

    def test_get_instance_raw(self, client):
        r = client.get('/api/instances/exemple_1_sujet?raw=true')
        assert r.status_code == 200
        data = r.get_json()
        assert "temps_prep" in data["plats"][0]
        assert "temps_cuisson" in data["plats"][0]

    def test_generate_instance(self, client):
        r = client.post('/api/instances/generate', json={
            "nombre_plats": 4, "nombre_commis": 2, "difficulte": "facile"
        })
        assert r.status_code == 200
        data = r.get_json()
        assert len(data["plats"]) == 4
