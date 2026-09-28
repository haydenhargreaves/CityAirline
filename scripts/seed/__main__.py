"""Run all database seed scripts in dependency order."""

import subprocess
import sys


SEED_MODULES = [
    "scripts.seed.airports",
    "scripts.seed.airlines",
    "scripts.seed.planes",
    "scripts.seed.passengers",
    "scripts.seed.flights",
    "scripts.seed.tickets",
    "scripts.seed.delays",
]


if __name__ == "__main__":
    for module in SEED_MODULES:
        print(f"Running {module}")
        subprocess.run([sys.executable, "-m", module], check=True)
