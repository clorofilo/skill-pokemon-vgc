import json
import math
import sys
from typing import Any

import click
from pydantic import BaseModel

from damage_calc import run_bridge, PokemonDef, CalcInput, FieldDef


class SurviveThreshold(BaseModel):
    type: str = "survive"
    attacker: PokemonDef
    move: str
    field: FieldDef = FieldDef()


class OutspeedThreshold(BaseModel):
    type: str = "outspeed"
    target_speed: int


class OptimizerInput(BaseModel):
    pokemon: PokemonDef
    targets: list[dict]


EV_STEPS = list(range(0, 253, 4))
DEFENSIVE_STATS = ["hp", "def", "spd"]

SPEED_BASES = {
    "Calyrex-Shadow": 150, "Flutter Mane": 135, "Chien-Pao": 135,
    "Iron Bundle": 136, "Urshifu": 97, "Urshifu-Rapid-Strike": 97,
    "Incineroar": 60, "Landorus-Therian": 91, "Tornadus": 111,
    "Rillaboom": 85, "Amoonguss": 30, "Farigiraf": 60, "Iron Hands": 50,
    "Miraidon": 135, "Koraidon": 98, "Calyrex-Ice": 50,
}

NATURE_MODIFIERS = {
    "Timid": 1.1, "Jolly": 1.1, "Hasty": 1.1, "Naive": 1.1,
    "Modest": 1.0, "Adamant": 1.0, "Bold": 1.0, "Careful": 1.0,
    "Quiet": 0.9, "Brave": 0.9, "Relaxed": 0.9, "Sassy": 0.9,
}


def calc_damage_with_evs(pokemon: PokemonDef, threshold: SurviveThreshold) -> dict:
    payload = CalcInput(
        attacker=threshold.attacker,
        defender=pokemon,
        move=threshold.move,
        field=threshold.field,
    )
    return run_bridge(payload.model_dump(by_alias=True))


def find_min_evs_to_survive(pokemon: PokemonDef, threshold: SurviveThreshold) -> dict:
    notes = []
    best_evs = {"hp": 252, "def": 0, "spd": 252}

    for hp in EV_STEPS:
        for spd in EV_STEPS:
            if hp + spd > 508:
                continue
            test_pokemon = pokemon.model_copy(update={"evs": {"hp": hp, "spd": spd}})
            result = calc_damage_with_evs(test_pokemon, threshold)
            ko_text = result.get("koText", "")
            if "guaranteed" not in ko_text and "1HKO" not in ko_text:
                if hp + spd < best_evs["hp"] + best_evs["spd"]:
                    best_evs = {"hp": hp, "def": 0, "spd": spd}
                    notes.append(f"Survives with {hp} HP / {spd} SpD")
                    break
        else:
            continue
        break

    return {"evs": best_evs, "remaining": 508 - sum(best_evs.values()), "notes": notes}


@click.command()
def main():
    """Optimize EV spreads. Reads OptimizerInput JSON from stdin, writes result to stdout."""
    raw = sys.stdin.read()
    opt_input = OptimizerInput.model_validate_json(raw)

    result_evs: dict[str, int] = {}
    all_notes: list[str] = []

    for target_raw in opt_input.targets:
        if target_raw.get("type") == "survive":
            threshold = SurviveThreshold.model_validate(target_raw)
            res = find_min_evs_to_survive(opt_input.pokemon, threshold)
            for stat, val in res["evs"].items():
                result_evs[stat] = max(result_evs.get(stat, 0), val)
            all_notes.extend(res["notes"])
        elif target_raw.get("type") == "outspeed":
            target_speed = target_raw.get("target_speed", 0)
            base_spe = SPEED_BASES.get(opt_input.pokemon.species, 80)
            nat_mod = NATURE_MODIFIERS.get(opt_input.pokemon.nature or "", 1.0)

            min_spe_evs = None
            for spe_evs in range(0, 253, 4):
                stat = math.floor((base_spe * 2 + 31 + math.floor(spe_evs / 4)) * 50 / 100 + 5)
                actual = math.floor(stat * nat_mod)
                if actual > target_speed:
                    min_spe_evs = spe_evs
                    break

            if min_spe_evs is not None:
                result_evs["spe"] = max(result_evs.get("spe", 0), min_spe_evs)
                all_notes.append(f"Needs {min_spe_evs} Spe EVs to outspeed {target_speed}")
            else:
                all_notes.append(f"Cannot outspeed {target_speed} even with 252 Spe EVs")

    total_used = sum(result_evs.values())
    print(json.dumps({
        "evs": result_evs,
        "remaining": max(0, 508 - total_used),
        "notes": all_notes,
    }))


if __name__ == "__main__":
    main()
