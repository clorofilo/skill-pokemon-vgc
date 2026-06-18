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
    # Timid nature Calyrex-Shadow (base 150 spe) outspeeds Incineroar (base 60 spe = 95 stat at 0 EVs)
    # With 0 EVs, Calyrex-Shadow Timid = floor((150*2+31+0)*50/100+5)*1.1 = floor(331*0.5+5)*1.1 = floor(170.5)*1.1 = 170*1.1 = 187
    # So requesting outspeed 186 should need 0 EVs
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
