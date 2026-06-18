import json
import re
import sys
from dataclasses import dataclass, field, asdict

import click

# Gen 9 type chart (attacking type -> {defending type -> multiplier})
TYPE_CHART: dict[str, dict[str, float]] = {
    "Fire": {"Grass": 2, "Ice": 2, "Bug": 2, "Steel": 2,
             "Fire": 0.5, "Water": 0.5, "Rock": 0.5, "Dragon": 0.5},
    "Water": {"Fire": 2, "Ground": 2, "Rock": 2,
              "Water": 0.5, "Grass": 0.5, "Dragon": 0.5},
    "Grass": {"Water": 2, "Ground": 2, "Rock": 2,
              "Fire": 0.5, "Grass": 0.5, "Poison": 0.5, "Flying": 0.5, "Bug": 0.5, "Dragon": 0.5, "Steel": 0.5},
    "Electric": {"Water": 2, "Flying": 2, "Electric": 0.5, "Grass": 0.5, "Dragon": 0.5, "Ground": 0},
    "Ice": {"Grass": 2, "Ground": 2, "Flying": 2, "Dragon": 2,
            "Fire": 0.5, "Water": 0.5, "Ice": 0.5, "Steel": 0.5},
    "Fighting": {"Normal": 2, "Ice": 2, "Rock": 2, "Dark": 2, "Steel": 2,
                 "Poison": 0.5, "Bug": 0.5, "Psychic": 0.5, "Flying": 0.5, "Fairy": 0.5, "Ghost": 0},
    "Poison": {"Grass": 2, "Fairy": 2, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Steel": 0},
    "Ground": {"Fire": 2, "Electric": 2, "Poison": 2, "Rock": 2, "Steel": 2,
               "Grass": 0.5, "Bug": 0.5, "Flying": 0},
    "Flying": {"Grass": 2, "Fighting": 2, "Bug": 2, "Electric": 0.5, "Rock": 0.5, "Steel": 0.5},
    "Psychic": {"Fighting": 2, "Poison": 2, "Psychic": 0.5, "Steel": 0.5, "Dark": 0},
    "Bug": {"Grass": 2, "Psychic": 2, "Dark": 2,
            "Fire": 0.5, "Fighting": 0.5, "Flying": 0.5, "Ghost": 0.5, "Steel": 0.5, "Fairy": 0.5},
    "Rock": {"Fire": 2, "Ice": 2, "Flying": 2, "Bug": 2,
             "Fighting": 0.5, "Ground": 0.5, "Steel": 0.5},
    "Ghost": {"Psychic": 2, "Ghost": 2, "Normal": 0, "Dark": 0.5},
    "Dragon": {"Dragon": 2, "Steel": 0.5, "Fairy": 0},
    "Dark": {"Psychic": 2, "Ghost": 2, "Fighting": 0.5, "Dark": 0.5, "Fairy": 0.5},
    "Steel": {"Ice": 2, "Rock": 2, "Fairy": 2,
              "Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Steel": 0.5,
              "Poison": 0, "Normal": 0.5},
    "Fairy": {"Fighting": 2, "Dragon": 2, "Dark": 2,
              "Fire": 0.5, "Poison": 0.5, "Steel": 0.5},
    "Normal": {"Rock": 0.5, "Steel": 0.5, "Ghost": 0},
}

SPEED_CONTROL_MOVES = {"Tailwind", "Trick Room", "Icy Wind", "Thunder Wave",
                        "Electroweb", "Glacial Lance", "String Shot"}


@dataclass
class TeamMember:
    species: str
    item: str = ""
    ability: str = ""
    nature: str = ""
    evs: dict = field(default_factory=dict)
    moves: list = field(default_factory=list)
    tera_type: str = ""


def parse_showdown_paste(paste: str) -> list[TeamMember]:
    members = []
    blocks = re.split(r'\n\n+', paste.strip())
    for block in blocks:
        lines = [l.strip() for l in block.strip().split('\n') if l.strip()]
        if not lines:
            continue
        m = re.match(r'^(.+?)(?:\s*@\s*(.+))?$', lines[0])
        if not m:
            continue
        species = m.group(1).strip().split('(')[0].strip()
        item = m.group(2).strip() if m.group(2) else ""
        member = TeamMember(species=species, item=item)
        for line in lines[1:]:
            if line.startswith("Ability:"):
                member.ability = line[8:].strip()
            elif line.startswith("EVs:"):
                for ev in line[4:].split('/'):
                    ev = ev.strip()
                    parts = ev.split(' ')
                    if len(parts) == 2:
                        stat_map = {"HP": "hp", "Atk": "atk", "Def": "def",
                                    "SpA": "spa", "SpD": "spd", "Spe": "spe"}
                        member.evs[stat_map.get(parts[1], parts[1].lower())] = int(parts[0])
            elif line.endswith("Nature"):
                member.nature = line.replace("Nature", "").strip()
            elif line.startswith("Tera Type:"):
                member.tera_type = line[10:].strip()
            elif line.startswith("- "):
                member.moves.append(line[2:].strip())
        members.append(member)
    return members


def find_speed_control(members: list[TeamMember]) -> list[str]:
    found = []
    for m in members:
        for move in m.moves:
            if move in SPEED_CONTROL_MOVES:
                found.append(f"{m.species}: {move}")
    return found


def find_type_weaknesses(members: list[TeamMember]) -> dict[str, list[str]]:
    weaknesses: dict[str, list[str]] = {}
    # MVP stub: full type weakness lookup requires a species->types map.
    # To extend: load types from data/formats/ or @smogon/data, then compute
    # multiplier products across all team members per attacking type.
    return weaknesses


@click.command()
def main():
    """Analyze a Showdown team paste. Reads JSON {team_paste} from stdin."""
    raw = sys.stdin.read()
    data = json.loads(raw)
    members = parse_showdown_paste(data["team_paste"])

    speed_control = find_speed_control(members)
    notes = []
    if not speed_control:
        notes.append("No speed control moves detected")

    print(json.dumps({
        "members": [asdict(m) for m in members],
        "type_weaknesses": find_type_weaknesses(members),
        "speed_control": speed_control,
        "speed_tiers": [],
        "notes": notes,
    }))


if __name__ == "__main__":
    main()
