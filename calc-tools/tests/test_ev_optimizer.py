import subprocess, json
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "ev_optimizer.py"
CALC_DIR = Path(__file__).parent.parent

def run_optimizer(payload):
    r = subprocess.run(["python", str(SCRIPT)], input=json.dumps(payload),
                       capture_output=True, text=True, cwd=str(CALC_DIR))
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)

def test_survive_threshold_returns_evs():
    payload = {
        "pokemon": {"species": "Incineroar", "item": "Assault Vest", "nature": "Careful"},
        "targets": [{
            "type": "survive",
            "attacker": {"species": "Calyrex-Shadow", "item": "Choice Specs",
                         "nature": "Timid", "evs": {"spa": 252, "spe": 252, "hp": 4},
                         "teraType": "Psychic"},
            "move": "Astral Barrage"
        }]
    }
    result = run_optimizer(payload)
    assert "evs" in result
    assert result["evs"]["hp"] + result["evs"]["spd"] <= 252 * 2
    assert "remaining" in result

def test_outspeed_threshold_returns_spe_evs():
    # Timid Calyrex-Shadow (base 150) at 0 EVs reaches 187 — already outspeeds 120.
    payload = {
        "pokemon": {"species": "Calyrex-Shadow", "item": "Choice Specs", "nature": "Timid"},
        "targets": [{"type": "outspeed", "target_speed": 120}]
    }
    result = run_optimizer(payload)
    assert "evs" in result
    assert "spe" in result["evs"]
    assert result["evs"]["spe"] >= 0
    assert "notes" in result
    assert any("spe" in note.lower() or "outspeed" in note.lower() for note in result["notes"])


def test_outspeed_needs_zero_evs_when_already_fast():
    # Timid Calyrex-Shadow base 150 at 0 EVs = 187; 0 EVs sufficient to outspeed 100
    payload = {
        "pokemon": {"species": "Calyrex-Shadow", "item": "Life Orb", "nature": "Timid"},
        "targets": [{"type": "outspeed", "target_speed": 100}]
    }
    result = run_optimizer(payload)
    assert result["evs"].get("spe", 0) == 0


def test_outspeed_impossible_emits_note():
    # Sassy Amoonguss (base 30, ×0.9 modifier) maxes at floor(floor((30*2+31+63)*50/100+5)*0.9)=73
    # Cannot outspeed target_speed 150
    payload = {
        "pokemon": {"species": "Amoonguss", "item": "Rocky Helmet", "nature": "Sassy"},
        "targets": [{"type": "outspeed", "target_speed": 150}]
    }
    result = run_optimizer(payload)
    assert "spe" not in result["evs"]
    assert any("Cannot outspeed" in note for note in result["notes"])


def test_remaining_evs_is_correct():
    payload = {
        "pokemon": {"species": "Incineroar", "item": "Assault Vest", "nature": "Careful"},
        "targets": [{
            "type": "survive",
            "attacker": {
                "species": "Calyrex-Shadow", "item": "Choice Specs",
                "nature": "Timid", "evs": {"spa": 252, "spe": 252, "hp": 4},
                "teraType": "Psychic",
            },
            "move": "Astral Barrage",
        }]
    }
    result = run_optimizer(payload)
    total_used = sum(result["evs"].values())
    assert result["remaining"] == max(0, 508 - total_used)
