# 🏆 Bot Benchmark & Score Tracker Report

This file tracks and compares match performances across different bot strategies.

## Matchup Results Overview

| Match ID | Player 1 | Player 2 | Score (P1 vs P2) | Winner | Margin | Duration |
| :---: | :--- | :--- | :---: | :--- | :---: | :---: |
| 1 | main.py (Current v2 Agent) | v1_main.py (Previous v1 Agent) | 1936 vs 6272 | **v1_main.py (Previous v1 Agent)** | +4336 | 2.61s |
| 2 | main.py (Current v2 Agent) | new_main.py (Single Farmer Baseline) | 4167 vs 2670 | **main.py (Current v2 Agent)** | +1497 | 1.86s |
| 3 | v1_main.py (Previous v1 Agent) | new_main.py (Single Farmer Baseline) | 8257 vs 2670 | **v1_main.py (Previous v1 Agent)** | +5587 | 2.07s |
| 4 | main.py (Current v2 Agent) | starter (Built-in Starter) | 3200 vs 3511 | **starter (Built-in Starter)** | +311 | 1.82s |
| 5 | v1_main.py (Previous v1 Agent) | starter (Built-in Starter) | 7549 vs 3487 | **v1_main.py (Previous v1 Agent)** | +4062 | 2.1s |
| 6 | main.py (Current v2 Agent) | random (Built-in Random) | 3593 vs 0 | **main.py (Current v2 Agent)** | +3593 | 1.9s |

## Strategic Takeaways

- **`main.py (v2)` vs `v1_main.py (v1)`**: Tests land expansion timing and worker scaling optimizations.
- **Multi-Worker Advantage**: Utilizing farm hands ($1/day) significantly increases total crop harvests per day.
- **Land Expansion & End-Game Cutoff**: Expanding land and stopping late seed purchases boosts final score substantially.