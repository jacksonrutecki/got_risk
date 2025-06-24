import json


with open("data/territories.json", "r") as f:
    TERRITORIES = json.load(f)


PHASES = {
    -2: "Move Armies",
    -1: "Board Setup",
    0: "Reinforce",
    1: "Invade",
    2: "Maneuver",
    3: "Draw"
}
