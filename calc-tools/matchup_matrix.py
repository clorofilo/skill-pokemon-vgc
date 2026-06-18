import json
import sys

import click

from team_analyzer import parse_showdown_paste


THREAT_EFFECTIVENESS: dict[str, dict[str, str]] = {
    "Calyrex-Shadow": {
        "Incineroar": "neutral",
        "Flutter Mane": "unfavorable",
        "Amoonguss": "favorable",
    },
    "Flutter Mane": {
        "Incineroar": "neutral",
        "Amoonguss": "favorable",
    },
}


def get_matchup(pokemon: str, threat: str) -> str:
    threat_data = THREAT_EFFECTIVENESS.get(threat, {})
    return threat_data.get(pokemon, "unknown")


@click.command()
def main():
    """Generate matchup matrix. Reads {team_paste, threats} JSON from stdin."""
    raw = sys.stdin.read()
    data = json.loads(raw)
    members = parse_showdown_paste(data["team_paste"])
    threats: list[str] = data.get("threats", [])

    matrix: dict[str, dict[str, str]] = {}
    for member in members:
        matrix[member.species] = {}
        for threat in threats:
            matrix[member.species][threat] = get_matchup(member.species, threat)

    favorable = sum(1 for row in matrix.values() for v in row.values() if v == "favorable")
    unfavorable = sum(1 for row in matrix.values() for v in row.values() if v == "unfavorable")

    print(json.dumps({
        "matrix": matrix,
        "summary": [
            f"Favorable matchups: {favorable}",
            f"Unfavorable matchups: {unfavorable}",
        ],
    }))


if __name__ == "__main__":
    main()
