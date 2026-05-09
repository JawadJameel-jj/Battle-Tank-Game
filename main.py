# ─────────────────────────────────────────────
#  main.py  –  Entry point
# ─────────────────────────────────────────────
# Battle City — AL2002 AI Lab Project
# Run with:  python main.py

# Controls:
#   WASD / Arrow keys  →  Move tank
#   SPACE              →  Shoot
#   P                  →  Pause
#   N                  →  Next level (after victory)
#   R                  →  Restart current level
#   ESC                →  Quit
 
import sys
import os

# Make sure all module imports resolve correctly regardless of working directory
sys.path.insert(0, os.path.dirname(__file__))

from core.game import Game


if __name__ == '__main__':
    game = Game()
    game.run()
