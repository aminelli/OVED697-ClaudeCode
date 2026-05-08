"""
Test per le Skill — verifica definizioni e implementazioni.

Non richiede API key: le skill sono puro Python deterministico.
"""

import json
import pytest
from pathlib import Path

from src.skills.file_skills import get_file_skill_definitions, execute_file_skill
from src.skills.data_skills import get_data_skill_definitions, execute_data_skill
from src.skills.registry import SkillRegistry
from src.artifacts.manager import ArtifactManager


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

CSV_SAMPLE = """product_id,product_name,category,units_sold,revenue,region
P001,Laptop,Electronics,100,150000,Nord
P002,Mouse,Electronics,500,25000,Sud
P003,Desk,Furniture,50,35000,Centro
P004,Chair,Furniture,80,48000,Nord
"""


@pytest.fixture
def tmp_csv(tmp_path: Path) -> Path:
    """File CSV temporaneo per i test."""
    f = tmp_path / "test_data.csv"
    f.write_text(CSV_SAMPLE, encoding="utf-8")
    return f


# ---------------------------------------------------------------------------
# Test: definizioni skill (struttura JSON)
# ---------------------------------------------------------------------------

class TestSkillDefinitions:
    def test_file_skills_have_required_fields(self):
        for skill in get_file_skill_definitions():
            assert "name" in skill
            assert "description" in skill
            assert "input_schema" in skill
            assert skill["input_schema"]["type"] == "object"
            assert "properties" in skill["input_schema"]

    def test_data_skills_have_required_fields(self):
        for skill in get_data_skill_definitions():
            assert "name" in skill
            assert "description" in skill
            assert "input_schema" in skill

    def test_skill_names_are_unique(self):
        all_defs = get_file_skill_definitions() + get_data_skill_definitions()
        names = [d["name"] for d in all_defs]
        assert len(names) == len(set(names)), "Nomi di skill duplicati!"

    def test_required_fields_are_subset_of_properties(self):
        """I required fields devono essere definiti nelle properties."""
        for skill in get_file_skill_definitions() + get_data_skill_definitions():
            schema = skill["input_schema"]
            props = set(schema.get("properties", {}).keys())
            required = set(schema.get("required", []))
            assert required.issubset(props), f"Skill {skill['name']}: required non in properties"


# ---------------------------------------------------------------------------
# Test: file skills
# ---------------------------------------------------------------------------

class TestFileSkills:
    def test_read_existing_file(self, tmp_csv: Path):
        result = execute_file_skill("read_text_file", {"filepath": str(tmp_csv)})
        assert "product_id" in result
        assert "Laptop" in result

    def test_read_nonexistent_file(self, tmp_path: Path):
        result = execute_file_skill("read_text_file", {"filepath": str(tmp_path / "nope.csv")})
        assert result.startswith("ERROR:")

    def test_list_directory(self, tmp_csv: Path):
        result = execute_file_skill("list_directory", {"directory": str(tmp_csv.parent)})
        assert "test_data.csv" in result

    def test_list_directory_with_extension(self, tmp_csv: Path):
        result = execute_file_skill(
            "list_directory",
            {"directory": str(tmp_csv.parent), "extension": ".csv"}
        )
        assert "test_data.csv" in result

    def test_list_directory_wrong_extension(self, tmp_csv: Path):
        result = execute_file_skill(
            "list_directory",
            {"directory": str(tmp_csv.parent), "extension": ".json"}
        )
        assert "Nessun file trovato" in result

    def test_unknown_skill_returns_error(self):
        result = execute_file_skill("nonexistent_skill", {})
        assert result.startswith("ERROR:")


# ---------------------------------------------------------------------------
# Test: data skills
# ---------------------------------------------------------------------------

class TestDataSkills:
    def test_parse_csv_schema(self):
        result = execute_data_skill("parse_csv_schema", {"csv_content": CSV_SAMPLE})
        schema = json.loads(result)
        assert "columns" in schema
        assert "product_id" in schema["columns"]
        assert schema["row_count"] == 4

    def test_parse_csv_schema_detects_numeric(self):
        result = execute_data_skill("parse_csv_schema", {"csv_content": CSV_SAMPLE})
        schema = json.loads(result)
        assert schema["column_types"]["revenue"] == "numeric"
        assert schema["column_types"]["product_name"] == "text"

    def test_compute_column_stats(self):
        result = execute_data_skill(
            "compute_column_stats",
            {"csv_content": CSV_SAMPLE, "column_name": "revenue"}
        )
        stats = json.loads(result)
        assert stats["sum"] == pytest.approx(258000)
        assert stats["count"] == 4
        assert stats["min"] == 25000
        assert stats["max"] == 150000

    def test_compute_stats_invalid_column(self):
        result = execute_data_skill(
            "compute_column_stats",
            {"csv_content": CSV_SAMPLE, "column_name": "colonna_inesistente"}
        )
        assert result.startswith("ERROR:")

    def test_aggregate_by_category(self):
        result = execute_data_skill(
            "aggregate_by_category",
            {
                "csv_content": CSV_SAMPLE,
                "group_column": "category",
                "value_column": "revenue",
            }
        )
        agg = json.loads(result)
        groups = {g["category"]: g["total"] for g in agg["groups"]}
        assert groups["Electronics"] == pytest.approx(175000)
        assert groups["Furniture"] == pytest.approx(83000)

    def test_aggregate_sorted_descending(self):
        """I gruppi devono essere ordinati per totale decrescente."""
        result = execute_data_skill(
            "aggregate_by_category",
            {
                "csv_content": CSV_SAMPLE,
                "group_column": "category",
                "value_column": "revenue",
            }
        )
        agg = json.loads(result)
        totals = [g["total"] for g in agg["groups"]]
        assert totals == sorted(totals, reverse=True)

    def test_data_skills_are_deterministic(self):
        """Stessa input → stesso output (requisito idempotenza)."""
        r1 = execute_data_skill("parse_csv_schema", {"csv_content": CSV_SAMPLE})
        r2 = execute_data_skill("parse_csv_schema", {"csv_content": CSV_SAMPLE})
        assert r1 == r2


# ---------------------------------------------------------------------------
# Test: SkillRegistry
# ---------------------------------------------------------------------------

class TestSkillRegistry:
    def test_registry_has_all_skills(self, tmp_path: Path):
        mgr = ArtifactManager(str(tmp_path / "out"))
        registry = SkillRegistry(artifact_manager=mgr)
        names = registry.tool_names()

        # Deve contenere almeno una skill per gruppo
        assert any("file" in n or "read" in n or "list" in n for n in names)
        assert any("csv" in n or "stat" in n or "aggr" in n for n in names)
        assert any("artifact" in n for n in names)

    def test_registry_dispatches_file_skill(self, tmp_csv: Path, tmp_path: Path):
        mgr = ArtifactManager(str(tmp_path / "out"))
        registry = SkillRegistry(artifact_manager=mgr)

        result = registry.execute("read_text_file", {"filepath": str(tmp_csv)})
        assert "product_id" in result

    def test_registry_dispatches_data_skill(self, tmp_path: Path):
        mgr = ArtifactManager(str(tmp_path / "out"))
        registry = SkillRegistry(artifact_manager=mgr)

        result = registry.execute("parse_csv_schema", {"csv_content": CSV_SAMPLE})
        schema = json.loads(result)
        assert schema["row_count"] == 4

    def test_registry_unknown_skill(self, tmp_path: Path):
        mgr = ArtifactManager(str(tmp_path / "out"))
        registry = SkillRegistry(artifact_manager=mgr)
        result = registry.execute("skill_inesistente", {})
        assert "ERROR" in result

    def test_registry_subset_of_groups(self, tmp_path: Path):
        """Registry con solo skill 'data' non deve avere file skill."""
        mgr = ArtifactManager(str(tmp_path / "out"))
        registry = SkillRegistry(artifact_manager=mgr, enabled_groups=["data"])
        names = registry.tool_names()
        assert "read_text_file" not in names
        assert "parse_csv_schema" in names
