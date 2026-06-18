import subprocess
import json
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "damage_calc.py"
CALC_DIR = Path(__file__).parent.parent

def run_calc(payload: dict) -> dict:
    result = subprocess.run(
        ["python", str(SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(CALC_DIR),
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    return json.loads(result.stdout)

def test_basic_damage_has_required_fields():
    payload = {
        "attacker": {
            "species": "Calyrex-Shadow",
            "item": "Choice Specs",
            "nature": "Timid",
            "evs": {"spa": 252, "spe": 252, "hp": 4},
            "teraType": "Psychic",
        },
        "defender": {
            "species": "Incineroar",
            "item": "Assault Vest",
            "nature": "Careful",
            "evs": {"hp": 252, "spd": 252, "atk": 4},
        },
        "move": "Astral Barrage",
    }
    result = run_calc(payload)
    assert "description" in result
    assert "damage" in result
    assert "koText" in result
    assert isinstance(result["damage"], list)
    assert len(result["damage"]) > 0

def test_damage_increases_with_attack_evs():
    base = {
        "attacker": {"species": "Iron Hands", "nature": "Adamant", "evs": {"atk": 0}, "item": "Assault Vest"},
        "defender": {"species": "Incineroar", "nature": "Careful", "evs": {"hp": 252, "spd": 252}, "item": "Assault Vest"},
        "move": "Close Combat",
    }
    high = json.loads(json.dumps(base))
    high["attacker"]["evs"] = {"atk": 252}

    r_base = run_calc(base)
    r_high = run_calc(high)
    assert r_high["max"] > r_base["max"]


def test_output_has_percent_and_kochance_fields():
    payload = {
        "attacker": {
            "species": "Flutter Mane", "item": "Choice Specs", "nature": "Timid",
            "evs": {"spa": 252, "spe": 252, "hp": 4},
        },
        "defender": {
            "species": "Incineroar", "item": "Assault Vest", "nature": "Careful",
            "evs": {"hp": 252, "spd": 252, "atk": 4},
        },
        "move": "Moonblast",
    }
    result = run_calc(payload)
    assert "minPercent" in result
    assert "maxPercent" in result
    assert "." in result["minPercent"]
    assert "." in result["maxPercent"]
    assert float(result["minPercent"]) <= float(result["maxPercent"])
    assert "koChance" in result
    assert "/" in result["koChance"]
    assert result["min"] <= result["max"]


def test_field_condition_does_not_crash():
    payload = {
        "attacker": {
            "species": "Calyrex-Shadow", "item": "Choice Specs", "nature": "Timid",
            "evs": {"spa": 252, "spe": 252, "hp": 4},
        },
        "defender": {
            "species": "Incineroar", "item": "Assault Vest", "nature": "Careful",
            "evs": {"hp": 252},
        },
        "move": "Astral Barrage",
        "field": {"weather": "Sun", "terrain": None},
    }
    result = run_calc(payload)
    assert "damage" in result
    assert isinstance(result["damage"], list) and len(result["damage"]) > 0
