# 🏆 Bot Benchmark & Score Tracker Report

This file tracks and compares match performances across different bot strategies.

## Matchup Results Overview

| Match ID | Player 1 | Player 2 | Score (P1 vs P2) | Winner | Margin | Duration |
| :---: | :--- | :--- | :---: | :--- | :---: | :---: |
| 1 | main.py (Current v2 Agent) | v1_main.py (Previous v1 Agent) | 5843 vs 5994 | **v1_main.py (Previous v1 Agent)** | +151 | 2.85s |
| 2 | main.py (Current v2 Agent) | new_main.py (Single Farmer Baseline) | 9155 vs 2670 | **main.py (Current v2 Agent)** | +6485 | 2.12s |
| 3 | v1_main.py (Previous v1 Agent) | new_main.py (Single Farmer Baseline) | 7599 vs 2670 | **v1_main.py (Previous v1 Agent)** | +4929 | 2.1s |
| 4 | main.py (Current v2 Agent) | starter (Built-in Starter) | 7730 vs 3499 | **main.py (Current v2 Agent)** | +4231 | 2.03s |
| 5 | v1_main.py (Previous v1 Agent) | starter (Built-in Starter) | 7864 vs 3514 | **v1_main.py (Previous v1 Agent)** | +4350 | 2.1s |
| 6 | main.py (Current v2 Agent) | random (Built-in Random) | 7763 vs 0 | **main.py (Current v2 Agent)** | +7763 | 2.2s |

## Strategic Takeaways

- **`main.py (v2)` vs `v1_main.py (v1)`**: Tests land expansion timing and worker scaling optimizations.
- **Multi-Worker Advantage**: Utilizing farm hands ($1/day) significantly increases total crop harvests per day.
- **Land Expansion & End-Game Cutoff**: Expanding land and stopping late seed purchases boosts final score substantially.