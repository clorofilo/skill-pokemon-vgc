import subprocess, json
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "team_analyzer.py"
SAMPLE_PASTE = """
Incineroar @ Assault Vest
Ability: Intimidate
EVs: 252 HP / 4 Atk / 252 SpD
Careful Nature
- Fake Out
- Knock Off
- U-turn
- Flare Blitz

Flutter Mane @ Choice Specs
Ability: Protosynthesis
EVs: 4 HP / 252 SpA / 252 Spe
Timid Nature
- Moonblast
- Shadow Ball
- Dazzling Gleam
- Mystical Fire
""".strip()

def test_parse_team_returns_members():
    r = subprocess.run(["python", str(SCRIPT)], input=json.dumps({"team_paste": SAMPLE_PASTE}),
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    result = json.loads(r.stdout)
    assert "members" in result
    assert len(result["members"]) >= 2
    assert "type_weaknesses" in result
    assert "speed_control" in result
