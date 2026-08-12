# 🏆 Bot Benchmark & Score Tracker Report

This file tracks and compares match performances across different bot strategies.

## Matchup Results Overview

| Match ID | Player 1 | Player 2 | Score (P1 vs P2) | Winner | Margin | Duration |
| :---: | :--- | :--- | :---: | :--- | :---: | :---: |
| 1 | main.py (Current v2 Agent) | v1_main.py (Previous v1 Agent) | 5450 vs 5990 | **v1_main.py (Previous v1 Agent)** | +540 | 2.92s |
| 2 | main.py (Current v2 Agent) | new_main.py (Single Farmer Baseline) | 9054 vs 2670 | **main.py (Current v2 Agent)** | +6384 | 2.38s |
| 3 | v1_main.py (Previous v1 Agent) | new_main.py (Single Farmer Baseline) | 9571 vs 2670 | **v1_main.py (Previous v1 Agent)** | +6901 | 2.37s |
| 4 | main.py (Current v2 Agent) | starter (Built-in Starter) | 7328 vs 3514 | **main.py (Current v2 Agent)** | +3814 | 2.28s |
| 5 | v1_main.py (Previous v1 Agent) | starter (Built-in Starter) | 7150 vs 3507 | **v1_main.py (Previous v1 Agent)** | +3643 | 2.5s |
| 6 | main.py (Current v2 Agent) | random (Built-in Random) | 8140 vs 0 | **main.py (Current v2 Agent)** | +8140 | 2.51s |

## Strategic Takeaways

- **`main.py (v2)` vs `v1_main.py (v1)`**: Tests land expansion timing and worker scaling optimizations.
- **Multi-Worker Advantage**: Utilizing farm hands ($1/day) significantly increases total crop harvests per day.
- **Land Expansion & End-Game Cutoff**: Expanding land and stopping late seed purchases boosts final score substantially.