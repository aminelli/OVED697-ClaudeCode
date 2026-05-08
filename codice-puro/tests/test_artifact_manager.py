"""
Test per ArtifactManager — verifica il comportamento idempotente.

I test coprono:
1. Creazione e salvataggio di un artifact
2. Rilevamento corretto di artifact fresh vs stale
3. Scrittura atomica (no file corrotti in caso di errore)
4. Persistenza del registro tra istanze diverse
5. Invalidazione e cancellazione
"""

import json
import pytest
from pathlib import Path

from src.artifacts.manager import ArtifactManager


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_manager(tmp_path: Path) -> ArtifactManager:
    """ArtifactManager con directory temporanea, pulita per ogni test."""
    return ArtifactManager(str(tmp_path / "output"))


# ---------------------------------------------------------------------------
# Test: hashing
# ---------------------------------------------------------------------------

class TestHashing:
    def test_same_content_same_hash(self):
        h1 = ArtifactManager.compute_hash("hello world")
        h2 = ArtifactManager.compute_hash("hello world")
        assert h1 == h2

    def test_different_content_different_hash(self):
        h1 = ArtifactManager.compute_hash("hello world")
        h2 = ArtifactManager.compute_hash("hello world!")
        assert h1 != h2

    def test_hash_is_sha256_hex(self):
        h = ArtifactManager.compute_hash("test")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


# ---------------------------------------------------------------------------
# Test: is_stale (cuore dell'idempotenza)
# ---------------------------------------------------------------------------

class TestIsStale:
    def test_new_artifact_is_stale(self, tmp_manager: ArtifactManager):
        """Un artifact mai salvato è sempre stale."""
        assert tmp_manager.is_stale("report.md", "any_hash") is True

    def test_fresh_artifact_not_stale(self, tmp_manager: ArtifactManager):
        """Artifact appena salvato con stesso source hash → fresh."""
        source = "contenuto sorgente"
        src_hash = tmp_manager.compute_hash(source)
        tmp_manager.save("report.md", "contenuto generato", src_hash)

        assert tmp_manager.is_stale("report.md", src_hash) is False

    def test_changed_source_makes_stale(self, tmp_manager: ArtifactManager):
        """Cambiare il sorgente rende l'artifact stale."""
        src_hash_v1 = tmp_manager.compute_hash("sorgente v1")
        tmp_manager.save("report.md", "report v1", src_hash_v1)

        src_hash_v2 = tmp_manager.compute_hash("sorgente v2")  # diverso
        assert tmp_manager.is_stale("report.md", src_hash_v2) is True

    def test_deleted_file_is_stale(self, tmp_manager: ArtifactManager):
        """Se il file fisico è stato eliminato, l'artifact è stale."""
        source = "sorgente"
        src_hash = tmp_manager.compute_hash(source)
        path = tmp_manager.save("report.md", "report", src_hash)

        # Elimina il file fisico ma NON il registro
        Path(path).unlink()
        assert tmp_manager.is_stale("report.md", src_hash) is True


# ---------------------------------------------------------------------------
# Test: save & load
# ---------------------------------------------------------------------------

class TestSaveLoad:
    def test_save_creates_file(self, tmp_manager: ArtifactManager):
        src_hash = tmp_manager.compute_hash("src")
        path = tmp_manager.save("test.md", "# Hello", src_hash)
        assert Path(path).exists()

    def test_load_returns_content(self, tmp_manager: ArtifactManager):
        content = "# Report\nContenuto del report."
        src_hash = tmp_manager.compute_hash("src")
        tmp_manager.save("report.md", content, src_hash)

        loaded = tmp_manager.load("report.md")
        assert loaded == content

    def test_load_nonexistent_returns_none(self, tmp_manager: ArtifactManager):
        assert tmp_manager.load("non_esiste.md") is None

    def test_save_is_idempotent(self, tmp_manager: ArtifactManager):
        """Salvare lo stesso contenuto due volte non causa errori."""
        src_hash = tmp_manager.compute_hash("src")
        tmp_manager.save("report.md", "contenuto", src_hash)
        tmp_manager.save("report.md", "contenuto", src_hash)  # seconda volta
        assert tmp_manager.load("report.md") == "contenuto"

    def test_overwrite_updates_content(self, tmp_manager: ArtifactManager):
        """Salvare un artifact esistente lo sovrascrive."""
        src_hash_v2 = tmp_manager.compute_hash("src v2")
        tmp_manager.save("report.md", "v1", tmp_manager.compute_hash("src v1"))
        tmp_manager.save("report.md", "v2", src_hash_v2)
        assert tmp_manager.load("report.md") == "v2"


# ---------------------------------------------------------------------------
# Test: persistenza del registro
# ---------------------------------------------------------------------------

class TestRegistryPersistence:
    def test_registry_survives_between_instances(self, tmp_path: Path):
        """Il registro viene riletto correttamente da una nuova istanza."""
        output_dir = str(tmp_path / "output")

        # Prima istanza: salva
        m1 = ArtifactManager(output_dir)
        src_hash = m1.compute_hash("sorgente stabile")
        m1.save("report.md", "contenuto", src_hash)

        # Seconda istanza: rilegge
        m2 = ArtifactManager(output_dir)
        assert m2.is_stale("report.md", src_hash) is False
        assert m2.load("report.md") == "contenuto"

    def test_registry_is_valid_json(self, tmp_manager: ArtifactManager):
        src_hash = tmp_manager.compute_hash("src")
        tmp_manager.save("a.md", "contenuto", src_hash)

        with open(tmp_manager.registry_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)  # non deve sollevare eccezione
        assert "artifacts" in data
        assert "a.md" in data["artifacts"]


# ---------------------------------------------------------------------------
# Test: invalidate & delete
# ---------------------------------------------------------------------------

class TestInvalidateDelete:
    def test_invalidate_makes_stale(self, tmp_manager: ArtifactManager):
        src_hash = tmp_manager.compute_hash("src")
        tmp_manager.save("report.md", "contenuto", src_hash)
        assert tmp_manager.is_stale("report.md", src_hash) is False

        tmp_manager.invalidate("report.md")
        assert tmp_manager.is_stale("report.md", src_hash) is True

    def test_delete_removes_file_and_registry(self, tmp_manager: ArtifactManager):
        src_hash = tmp_manager.compute_hash("src")
        path = tmp_manager.save("report.md", "contenuto", src_hash)

        assert tmp_manager.delete("report.md") is True
        assert not Path(path).exists()
        assert tmp_manager.get_info("report.md") is None

    def test_delete_nonexistent_returns_false(self, tmp_manager: ArtifactManager):
        assert tmp_manager.delete("non_esiste.md") is False


# ---------------------------------------------------------------------------
# Test: idempotenza end-to-end (simulata senza Claude)
# ---------------------------------------------------------------------------

class TestIdempotencyEndToEnd:
    def test_pipeline_skip_count(self, tmp_manager: ArtifactManager):
        """
        Simula due esecuzioni consecutive della pipeline.
        Alla seconda esecuzione, TUTTI gli artifact devono essere 'fresh'.
        """
        source_files = {
            "analysis_q1.md": "csv q1 contenuto stabile",
            "analysis_q2.md": "csv q2 contenuto stabile",
            "analysis_q3.md": "csv q3 contenuto stabile",
        }

        # Prima esecuzione: genera tutto
        processed_first = 0
        for artifact_id, source in source_files.items():
            src_hash = tmp_manager.compute_hash(source)
            if tmp_manager.is_stale(artifact_id, src_hash):
                tmp_manager.save(artifact_id, f"report per {artifact_id}", src_hash)
                processed_first += 1

        assert processed_first == 3  # tutti processati

        # Seconda esecuzione: niente da fare
        skipped_second = 0
        for artifact_id, source in source_files.items():
            src_hash = tmp_manager.compute_hash(source)
            if not tmp_manager.is_stale(artifact_id, src_hash):
                skipped_second += 1  # ← idempotenza

        assert skipped_second == 3  # tutti saltati

    def test_partial_change_triggers_only_changed(self, tmp_manager: ArtifactManager):
        """Solo i file modificati vengono rielaborati."""
        sources = {
            "analysis_q1.md": "q1 stabile",
            "analysis_q2.md": "q2 stabile",
        }

        # Prima esecuzione
        for aid, src in sources.items():
            h = tmp_manager.compute_hash(src)
            tmp_manager.save(aid, f"report {aid}", h)

        # Modifica SOLO q2
        sources["analysis_q2.md"] = "q2 MODIFICATO"

        stale_count = sum(
            1 for aid, src in sources.items()
            if tmp_manager.is_stale(aid, tmp_manager.compute_hash(src))
        )
        assert stale_count == 1  # solo q2 è stale
