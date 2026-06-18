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
