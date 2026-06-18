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

FULL_TEAM_PASTE = """
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
Tera Type: Fairy
- Moonblast
- Shadow Ball
- Dazzling Gleam
- Mystical Fire

Rillaboom @ Assault Vest
Ability: Grassy Surge
EVs: 252 HP / 252 Atk / 4 Def
Adamant Nature
- Fake Out
- Wood Hammer
- U-turn
- High Horsepower

Landorus-Therian @ Leftovers
Ability: Intimidate
EVs: 252 HP / 4 Def / 252 Spe
Jolly Nature
- Earthquake
- Rock Slide
- U-turn
- Protect

Urshifu-Rapid-Strike @ Choice Band
Ability: Unseen Fist
EVs: 4 HP / 252 Atk / 252 Spe
Jolly Nature
- Surging Strikes
- Close Combat
- U-turn
- Aqua Jet

Amoonguss @ Rocky Helmet
Ability: Regenerator
EVs: 252 HP / 4 Def / 252 SpD
Sassy Nature
- Spore
- Pollen Puff
- Rage Powder
- Clear Smog
""".strip()

TAILWIND_PASTE = """
Tornadus @ Focus Sash
Ability: Prankster
EVs: 4 HP / 252 SpA / 252 Spe
Timid Nature
- Tailwind
- Hurricane
- Protect
- Taunt
""".strip()


def run_analyzer(paste: str) -> dict:
    r = subprocess.run(
        ["python", str(SCRIPT)],
        input=json.dumps({"team_paste": paste}),
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def test_parse_team_returns_members():
    result = run_analyzer(SAMPLE_PASTE)
    assert "members" in result
    assert len(result["members"]) >= 2
    assert "type_weaknesses" in result
    assert "speed_control" in result


def test_full_team_parses_all_six_members():
    result = run_analyzer(FULL_TEAM_PASTE)
    assert len(result["members"]) == 6
    species = [m["species"] for m in result["members"]]
    assert "Incineroar" in species
    assert "Flutter Mane" in species
    assert "Amoonguss" in species


def test_evs_parsed_correctly():
    result = run_analyzer(SAMPLE_PASTE)
    incineroar = result["members"][0]
    assert incineroar["evs"]["hp"] == 252
    assert incineroar["evs"]["spd"] == 252
    assert incineroar["evs"]["atk"] == 4


def test_tera_type_parsed():
    result = run_analyzer(FULL_TEAM_PASTE)
    flutter = next(m for m in result["members"] if m["species"] == "Flutter Mane")
    assert flutter["tera_type"] == "Fairy"


def test_speed_control_tailwind_detected():
    result = run_analyzer(TAILWIND_PASTE)
    assert any("Tailwind" in sc for sc in result["speed_control"])


def test_no_speed_control_emits_note():
    # Incineroar and Flutter Mane have no speed control moves
    result = run_analyzer(SAMPLE_PASTE)
    assert any("No speed control" in note for note in result["notes"])
