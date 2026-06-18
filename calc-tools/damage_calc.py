import json
import subprocess
import sys
from pathlib import Path

import click
from pydantic import BaseModel, Field

BRIDGE = Path(__file__).parent / "calc_bridge.js"


class EVSpread(BaseModel):
    hp: int = 0
    atk: int = 0
    def_: int = Field(0, alias="def")
    spa: int = 0
    spd: int = 0
    spe: int = 0

    model_config = {"populate_by_name": True}


class PokemonDef(BaseModel):
    species: str
    item: str | None = None
    nature: str | None = None
    evs: dict = {}
    teraType: str | None = None
    boosts: dict = {}


class FieldDef(BaseModel):
    weather: str | None = None
    terrain: str | None = None


class CalcInput(BaseModel):
    attacker: PokemonDef
    defender: PokemonDef
    move: str
    field: FieldDef = FieldDef()


def run_bridge(payload: dict) -> dict:
    result = subprocess.run(
        ["node", str(BRIDGE), json.dumps(payload)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        error = json.loads(result.stderr) if result.stderr.strip().startswith("{") else {"error": result.stderr}
        raise RuntimeError(f"calc_bridge error: {error}")
    return json.loads(result.stdout)


@click.command()
def main():
    """Calculate damage. Reads CalcInput JSON from stdin, writes CalcResult JSON to stdout."""
    raw = sys.stdin.read()
    calc_input = CalcInput.model_validate_json(raw)
    result = run_bridge(calc_input.model_dump(by_alias=True))
    print(json.dumps(result))


if __name__ == "__main__":
    main()
