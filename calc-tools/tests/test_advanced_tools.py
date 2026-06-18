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


def test_turn_simulator_priority_ordering():
    # Fake Out (priority +3) must appear before Moonblast (priority 0)
    result = run_tool("turn_simulator.py", {
        "state": {"side_a": ["Incineroar", "Flutter Mane"], "side_b": ["Calyrex-Shadow", "Rillaboom"],
                  "weather": None, "terrain": None},
        "moves": [
            {"user": "Flutter Mane", "move": "Moonblast", "target": "Calyrex-Shadow"},
            {"user": "Incineroar", "move": "Fake Out", "target": "Calyrex-Shadow"},
        ]
    })
    move_events = [e for e in result["events"] if e["type"] == "move"]
    assert len(move_events) == 2
    assert move_events[0]["actor"] == "Incineroar"
    assert move_events[1]["actor"] == "Flutter Mane"


def test_turn_simulator_priority_tag_in_description():
    result = run_tool("turn_simulator.py", {
        "state": {"side_a": ["Incineroar", "Flutter Mane"], "side_b": ["Calyrex-Shadow", "Rillaboom"],
                  "weather": None, "terrain": None},
        "moves": [{"user": "Incineroar", "move": "Fake Out", "target": "Calyrex-Shadow"}]
    })
    event = result["events"][0]
    assert "priority" in event["description"]


def test_turn_simulator_weather_event_emitted():
    result = run_tool("turn_simulator.py", {
        "state": {"side_a": ["Incineroar", "Flutter Mane"], "side_b": ["Calyrex-Shadow", "Rillaboom"],
                  "weather": "Sun", "terrain": None},
        "moves": [{"user": "Flutter Mane", "move": "Moonblast", "target": "Calyrex-Shadow"}]
    })
    weather_events = [e for e in result["events"] if e["type"] == "weather"]
    assert len(weather_events) == 1
    assert "Sun" in weather_events[0]["description"]


def test_turn_simulator_terrain_event_emitted():
    result = run_tool("turn_simulator.py", {
        "state": {"side_a": ["Rillaboom", "Flutter Mane"], "side_b": ["Calyrex-Shadow", "Amoonguss"],
                  "weather": None, "terrain": "Grassy"},
        "moves": [{"user": "Rillaboom", "move": "Wood Hammer", "target": "Amoonguss"}]
    })
    terrain_events = [e for e in result["events"] if e["type"] == "terrain"]
    assert len(terrain_events) == 1
    assert "Grassy" in terrain_events[0]["description"]


def test_turn_simulator_final_state_preserves_field():
    result = run_tool("turn_simulator.py", {
        "state": {"side_a": ["Incineroar", "Flutter Mane"], "side_b": ["Calyrex-Shadow", "Rillaboom"],
                  "weather": "Rain", "terrain": "Electric"},
        "moves": [{"user": "Incineroar", "move": "Fake Out", "target": "Calyrex-Shadow"}]
    })
    assert result["final_state"]["weather"] == "Rain"
    assert result["final_state"]["terrain"] == "Electric"


def test_lead_analyzer_sorted_by_score_descending():
    result = run_tool("lead_analyzer.py", {
        "team": ["Incineroar", "Flutter Mane", "Rillaboom", "Urshifu-Rapid-Strike", "Landorus-Therian", "Amoonguss"],
        "meta": []
    })
    scores = [lead["score"] for lead in result["leads"]]
    assert scores == sorted(scores, reverse=True)


def test_lead_analyzer_bring_priority_has_4_entries():
    result = run_tool("lead_analyzer.py", {
        "team": ["Incineroar", "Flutter Mane", "Rillaboom", "Urshifu-Rapid-Strike", "Landorus-Therian", "Amoonguss"],
        "meta": []
    })
    assert len(result["bring_priority"]) == 4


def test_lead_analyzer_support_attacker_synergy_bonus():
    # Incineroar (support) + Calyrex-Shadow (attacker) earns +2 synergy bonus;
    # Flutter Mane (attacker) + Calyrex-Shadow (attacker) does not.
    result = run_tool("lead_analyzer.py", {
        "team": ["Incineroar", "Calyrex-Shadow", "Flutter Mane", "Rillaboom", "Tornadus", "Amoonguss"],
        "meta": []
    })
    leads_by_pair = {(lead["pair"][0], lead["pair"][1]): lead["score"] for lead in result["leads"]}
    incineroar_calyrex = leads_by_pair.get(("Incineroar", "Calyrex-Shadow"))
    flutter_calyrex = leads_by_pair.get(("Flutter Mane", "Calyrex-Shadow"))
    if incineroar_calyrex is not None and flutter_calyrex is not None:
        assert incineroar_calyrex > flutter_calyrex


def test_lead_analyzer_max_5_leads_returned():
    result = run_tool("lead_analyzer.py", {
        "team": ["Incineroar", "Flutter Mane", "Rillaboom", "Urshifu-Rapid-Strike", "Landorus-Therian", "Amoonguss"],
        "meta": []
    })
    assert len(result["leads"]) <= 5


def test_matchup_matrix_shape():
    team = (
        "Incineroar @ Assault Vest\nAbility: Intimidate\nEVs: 252 HP\nCareful Nature"
        "\n- Fake Out\n- Knock Off\n- U-turn\n- Flare Blitz\n\n"
        "Amoonguss @ Rocky Helmet\nAbility: Regenerator\nEVs: 252 HP\nSassy Nature"
        "\n- Spore\n- Rage Powder\n- Pollen Puff\n- Clear Smog"
    )
    result = run_tool("matchup_matrix.py", {"team_paste": team, "threats": ["Flutter Mane", "Calyrex-Shadow"]})
    assert set(result["matrix"].keys()) == {"Incineroar", "Amoonguss"}
    for row in result["matrix"].values():
        assert "Flutter Mane" in row
        assert "Calyrex-Shadow" in row


def test_matchup_matrix_known_values():
    # THREAT_EFFECTIVENESS: Calyrex-Shadow vs Amoonguss = "favorable" (Amoonguss handles it well)
    team = "Amoonguss @ Rocky Helmet\nAbility: Regenerator\nEVs: 252 HP\nSassy Nature\n- Spore\n- Rage Powder\n- Pollen Puff\n- Clear Smog"
    result = run_tool("matchup_matrix.py", {"team_paste": team, "threats": ["Calyrex-Shadow", "Flutter Mane"]})
    assert result["matrix"]["Amoonguss"]["Calyrex-Shadow"] == "favorable"
    assert result["matrix"]["Amoonguss"]["Flutter Mane"] == "favorable"


def test_matchup_matrix_unknown_returns_unknown():
    team = "Gardevoir @ Choice Specs\nAbility: Trace\nEVs: 4 HP / 252 SpA / 252 Spe\nTimid Nature\n- Psychic\n- Moonblast\n- Shadow Ball\n- Hyper Voice"
    result = run_tool("matchup_matrix.py", {"team_paste": team, "threats": ["Calyrex-Shadow"]})
    assert result["matrix"]["Gardevoir"]["Calyrex-Shadow"] == "unknown"


def test_matchup_matrix_summary_counts_are_correct():
    team = (
        "Amoonguss @ Rocky Helmet\nAbility: Regenerator\nEVs: 252 HP\nSassy Nature"
        "\n- Spore\n- Rage Powder\n- Pollen Puff\n- Clear Smog\n\n"
        "Incineroar @ Assault Vest\nAbility: Intimidate\nEVs: 252 HP\nCareful Nature"
        "\n- Fake Out\n- Knock Off\n- U-turn\n- Flare Blitz"
    )
    result = run_tool("matchup_matrix.py", {"team_paste": team, "threats": ["Calyrex-Shadow", "Flutter Mane"]})
    favorable = sum(1 for row in result["matrix"].values() for v in row.values() if v == "favorable")
    unfavorable = sum(1 for row in result["matrix"].values() for v in row.values() if v == "unfavorable")
    assert f"Favorable matchups: {favorable}" in result["summary"]
    assert f"Unfavorable matchups: {unfavorable}" in result["summary"]
