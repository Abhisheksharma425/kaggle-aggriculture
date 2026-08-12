# 🏆 Bot Benchmark & Score Tracker Report

This file tracks and compares match performances across different bot strategies.

## Matchup Results Overview

| Match ID | Player 1 | Player 2 | Score (P1 vs P2) | Winner | Margin | Duration |
| :---: | :--- | :--- | :---: | :--- | :---: | :---: |
| 1 | main.py (Current v2 Agent) | v1_main.py (Previous v1 Agent) | 3541 vs 9014 | **v1_main.py (Previous v1 Agent)** | +5473 | 2.38s |
| 2 | main.py (Current v2 Agent) | new_main.py (Single Farmer Baseline) | 4256 vs 2670 | **main.py (Current v2 Agent)** | +1586 | 1.54s |
| 3 | v1_main.py (Previous v1 Agent) | new_main.py (Single Farmer Baseline) | 6728 vs 2670 | **v1_main.py (Previous v1 Agent)** | +4058 | 2.13s |
| 4 | main.py (Current v2 Agent) | starter (Built-in Starter) | 4159 vs 3483 | **main.py (Current v2 Agent)** | +676 | 1.76s |
| 5 | v1_main.py (Previous v1 Agent) | starter (Built-in Starter) | 6555 vs 3509 | **v1_main.py (Previous v1 Agent)** | +3046 | 2.28s |
| 6 | main.py (Current v2 Agent) | random (Built-in Random) | 4169 vs 0 | **main.py (Current v2 Agent)** | +4169 | 1.82s |

## Strategic Takeaways

- **`main.py (v2)` vs `v1_main.py (v1)`**: Tests land expansion timing and worker scaling optimizations.
- **Multi-Worker Advantage**: Utilizing farm hands ($1/day) significantly increases total crop harvests per day.
- **Land Expansion & End-Game Cutoff**: Expanding land and stopping late seed purchases boosts final score substantially.