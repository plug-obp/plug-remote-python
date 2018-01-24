from ga import VARIABLES, BEHAVIOURS, GUARD, ACTION, to_plug
import sys
from main import main

MAX = 1024

def inc_action(c):
    c["c"] = c["c"] + 1

def reset_action(c):
    c["c"] = 0

COUNTER_MODEL = {
    VARIABLES: {"c": 0},
    BEHAVIOURS: {
        "inc": {
            GUARD: lambda c: c["c"] < MAX,
            ACTION: inc_action
        },
        "reset": {
            GUARD: lambda c: c["c"] >= MAX,
            ACTION: reset_action
        }
    }
}

if __name__ == "__main__":
    main(sys.argv[1:], to_plug(COUNTER_MODEL))
