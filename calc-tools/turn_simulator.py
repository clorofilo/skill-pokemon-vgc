import json
import sys
from dataclasses import dataclass, asdict
from typing import Any

import click

PRIORITY_MOVES = {
    "Fake Out": 3, "Quick Attack": 1, "Extreme Speed": 2, "Sucker Punch": 1,
    "Aqua Jet": 1, "Bullet Punch": 1, "Mach Punch": 1, "Shadow Sneak": 1,
    "Ice Shard": 1, "Vacuum Wave": 1,
}

@dataclass
class TurnEvent:
    type: str
    actor: str
    description: str


def get_priority(move: str) -> int:
    return PRIORITY_MOVES.get(move, 0)


def simulate_turn(state: dict, moves: list[dict]) -> dict:
    events: list[TurnEvent] = []

    sorted_moves = sorted(moves, key=lambda m: -get_priority(m["move"]))

    for move_choice in sorted_moves:
        priority = get_priority(move_choice["move"])
        priority_tag = f" (priority +{priority})" if priority > 0 else ""
        events.append(TurnEvent(
            type="move",
            actor=move_choice["user"],
            description=f"{move_choice['user']} used {move_choice['move']} on {move_choice['target']}{priority_tag}",
        ))

    weather = state.get("weather")
    terrain = state.get("terrain")
    if weather:
        events.append(TurnEvent(type="weather", actor="field", description=f"{weather} continues"))
    if terrain:
        events.append(TurnEvent(type="terrain", actor="field", description=f"{terrain} pulses"))

    return {
        "events": [asdict(e) for e in events],
        "final_state": {"weather": weather, "terrain": terrain, "turn": "end"},
    }


@click.command()
def main():
    """Simulate a battle turn. Reads {state, moves} JSON from stdin."""
    raw = sys.stdin.read()
    data = json.loads(raw)
    result = simulate_turn(data["state"], data["moves"])
    print(json.dumps(result))


if __name__ == "__main__":
    main()
