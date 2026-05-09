# Battle City — AL2002 AI Lab Project

## Setup
```
pip install -r requirements.txt
python main.py
```

## Controls
| Key | Action |
|-----|--------|
| WASD / Arrow keys | Move |
| SPACE | Shoot |
| P | Pause |
| N | Next level (after winning) |
| R | Restart current level |
| ESC | Quit |

## Project Structure
```
battle_city/
├── main.py               ← entry point
├── settings.py           ← all constants
├── core/
│   ├── game.py           ← game loop, collision, win/lose
│   ├── grid.py           ← 26x26 tile map
│   ├── bullet.py         ← bullet movement & collision
│   └── spawner.py        ← enemy spawn management
├── tanks/
│   ├── base_tank.py      ← shared HP, movement, shooting
│   ├── player_tank.py    ← keyboard input
│   ├── basic_tank.py     ← Simple Reflex + BFS
│   ├── fast_tank.py      ← Goal-Based + Greedy Best-First
│   ├── armor_tank.py     ← Model-Based Reflex + A*
│   └── boss_tank.py      ← Adversarial + Minimax + Alpha-Beta
├── ai/
│   ├── bfs.py            ← Breadth-First Search
│   ├── greedy.py         ← Greedy Best-First Search
│   ├── astar.py          ← A* with terrain costs
│   └── minimax.py        ← Minimax + Alpha-Beta Pruning
├── csp/
│   ├── map_generator.py  ← CSP backtracking map generator
│   └── constraints.py    ← 5 CSP constraint checks
└── rendering/
    ├── renderer.py       ← pygame drawing
    └── hud.py            ← HUD (lives, score, minimax stats)
```

## AI Module Summary
| Module | Tank | Algorithm | Agent Type |
|--------|------|-----------|------------|
| B | Basic | BFS | Simple Reflex |
| B | Fast | Greedy Best-First | Goal-Based |
| B | Armor | A* | Model-Based Reflex |
| C | Boss | Minimax + Alpha-Beta | Adversarial |

## Minimax Stats (for report)
The HUD in the Boss level shows live:
- Minimax depth per phase (2 / 3 / 4)
- Nodes evaluated WITH Alpha-Beta pruning
- Nodes evaluated WITHOUT pruning
- Speedup ratio

Record these numbers for your project report's algorithm analysis section.
