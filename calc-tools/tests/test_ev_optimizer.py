import subprocess, sys, json
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "ev_optimizer.py"
CALC_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(CALC_DIR))
import ev_optimizer  # noqa: E402

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


def test_outspeed_unknown_species_flags_assumed_base_speed():
    # "Garchomp" is Reg M-B's #1 usage Pokémon but was missing from the local
    # SPEED_BASES table, silently falling back to base 80 with no indication
    # the number might be wrong.
    payload = {
        "pokemon": {"species": "Definitely-Not-A-Real-Species", "item": "Choice Scarf", "nature": "Jolly"},
        "targets": [{"type": "outspeed", "target_speed": 100}]
    }
    result = run_optimizer(payload)
    assert any("not in local table" in note.lower() or "assumed" in note.lower() for note in result["notes"])


def test_outspeed_garchomp_uses_correct_base_speed():
    # Garchomp base Speed is 102, not the 80 fallback.
    # Jolly (x1.1) at 0 EVs: floor((102*2+31)*50/100+5) = floor(122.5)=122 -> *1.1 -> floor(134.2)=134
    payload = {
        "pokemon": {"species": "Garchomp", "item": "Choice Band", "nature": "Jolly"},
        "targets": [{"type": "outspeed", "target_speed": 130}]
    }
    result = run_optimizer(payload)
    assert result["evs"].get("spe", 0) == 0
    assert not any("not in local table" in note.lower() for note in result["notes"])


def test_survive_search_finds_true_minimum_across_hp_values(monkeypatch):
    # Synthetic bulk model: survives iff 3*hp + spd >= 760 (HP is the more
    # EV-efficient stat here). At hp=0 no spd (max 252) can reach 760, so a
    # search that locks onto the *first* hp where some spd works stops at
    # hp=172/spd=244 (total 416) and never checks whether a larger hp beats
    # it. The true minimum is hp=252/spd=4 (total 256).
    def fake_calc(pokemon, threshold):
        hp = pokemon.evs.get("hp", 0)
        spd = pokemon.evs.get("spd", 0)
        survives = (3 * hp + spd) >= 760
        return {"koText": "" if survives else "guaranteed OHKO"}

    monkeypatch.setattr(ev_optimizer, "calc_damage_with_evs", fake_calc)

    pokemon = ev_optimizer.PokemonDef(species="Incineroar", nature="Careful")
    threshold = ev_optimizer.SurviveThreshold(
        attacker=ev_optimizer.PokemonDef(species="Calyrex-Shadow"),
        move="Astral Barrage",
    )
    result = ev_optimizer.find_min_evs_to_survive(pokemon, threshold)
    total = result["evs"]["hp"] + result["evs"]["spd"]
    assert total == 256
    assert result["evs"]["hp"] == 252
    assert result["evs"]["spd"] == 4


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
