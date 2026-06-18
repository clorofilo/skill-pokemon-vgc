import json
import sys
from itertools import combinations

import click


COMMON_LEADS = {
    "Incineroar": {"roles": ["support", "intimidate"], "lead_value": 8},
    "Flutter Mane": {"roles": ["attacker"], "lead_value": 7},
    "Calyrex-Shadow": {"roles": ["attacker"], "lead_value": 9},
    "Amoonguss": {"roles": ["support", "redirection"], "lead_value": 7},
    "Tornadus": {"roles": ["support", "tailwind"], "lead_value": 8},
    "Rillaboom": {"roles": ["support", "terrain"], "lead_value": 6},
    "Urshifu-Rapid-Strike": {"roles": ["attacker"], "lead_value": 8},
}


def score_lead_pair(p1: str, p2: str, meta: list[str]) -> float:
    d1 = COMMON_LEADS.get(p1, {"roles": [], "lead_value": 5})
    d2 = COMMON_LEADS.get(p2, {"roles": [], "lead_value": 5})
    score = (d1["lead_value"] + d2["lead_value"]) / 2
    roles = set(d1["roles"]) | set(d2["roles"])
    if "support" in roles and "attacker" in roles:
        score += 2
    return score


@click.command()
def main():
    """Analyze lead options. Reads {team, meta} JSON from stdin."""
    raw = sys.stdin.read()
    data = json.loads(raw)
    team: list[str] = data["team"]
    meta: list[str] = data.get("meta", [])

    lead_options = []
    for p1, p2 in combinations(team, 2):
        score = score_lead_pair(p1, p2, meta)
        lead_options.append({"pair": [p1, p2], "score": score, "note": ""})

    lead_options.sort(key=lambda x: -x["score"])

    print(json.dumps({
        "leads": lead_options[:5],
        "bring_priority": team[:4],
    }))


if __name__ == "__main__":
    main()
