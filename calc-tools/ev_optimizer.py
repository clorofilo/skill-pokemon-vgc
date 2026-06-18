import json
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

    total_used = sum(result_evs.values())
    print(json.dumps({
        "evs": result_evs,
        "remaining": max(0, 508 - total_used),
        "notes": all_notes,
    }))


if __name__ == "__main__":
    main()
