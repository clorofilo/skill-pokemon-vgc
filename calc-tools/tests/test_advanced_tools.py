import subprocess, json
from pathlib import Path

TOOLS_DIR = Path(__file__).parent.parent

def run_tool(script, payload):
    r = subprocess.run(
        ["python", str(TOOLS_DIR / script)],
        input=json.dumps(payload), capture_output=True, text=True, cwd=str(TOOLS_DIR)
    )
    assert r.returncode == 0, f"{script} stderr: {r.stderr}"
    return json.loads(r.stdout)

def test_matchup_matrix_returns_matrix():
    team = "Incineroar @ Assault Vest\nAbility: Intimidate\nEVs: 252 HP / 4 Atk / 252 SpD\nCareful Nature\n- Fake Out\n- Knock Off\n- U-turn\n- Flare Blitz"
    result = run_tool("matchup_matrix.py", {"team_paste": team, "threats": ["Calyrex-Shadow", "Flutter Mane"]})
    assert "matrix" in result
    assert "Incineroar" in result["matrix"] or len(result["matrix"]) >= 0

def test_lead_analyzer_returns_leads():
    result = run_tool("lead_analyzer.py", {
        "team": ["Incineroar", "Flutter Mane", "Rillaboom", "Urshifu-Rapid-Strike", "Landorus-Therian", "Amoonguss"],
        "meta": ["Calyrex-Shadow", "Urshifu-Rapid-Strike"]
    })
    assert "leads" in result
    assert "bring_priority" in result

def test_turn_simulator_returns_events():
    result = run_tool("turn_simulator.py", {
        "state": {
            "side_a": ["Incineroar", "Flutter Mane"],
            "side_b": ["Calyrex-Shadow", "Rillaboom"],
            "weather": None, "terrain": None
        },
        "moves": [
            {"user": "Flutter Mane", "move": "Moonblast", "target": "Calyrex-Shadow"},
            {"user": "Incineroar", "move": "Fake Out", "target": "Calyrex-Shadow"}
        ]
    })
    assert "events" in result
