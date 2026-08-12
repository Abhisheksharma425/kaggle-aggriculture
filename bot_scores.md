# 🏆 Bot Benchmark & Score Tracker Report

This file tracks and compares match performances across different bot strategies.

## Matchup Results Overview

| Match ID | Player 1 | Player 2 | Score (P1 vs P2) | Winner | Margin | Duration |
| :---: | :--- | :--- | :---: | :--- | :---: | :---: |
| 1 | main.py (Current v2 Agent) | v1_main.py (Previous v1 Agent) | 6720 vs 6593 | **main.py (Current v2 Agent)** | +127 | 2.91s |
| 2 | main.py (Current v2 Agent) | new_main.py (Single Farmer Baseline) | 8743 vs 2670 | **main.py (Current v2 Agent)** | +6073 | 2.33s |
| 3 | v1_main.py (Previous v1 Agent) | new_main.py (Single Farmer Baseline) | 9571 vs 2670 | **v1_main.py (Previous v1 Agent)** | +6901 | 2.41s |
| 4 | main.py (Current v2 Agent) | starter (Built-in Starter) | 6974 vs 3427 | **main.py (Current v2 Agent)** | +3547 | 2.37s |
| 5 | v1_main.py (Previous v1 Agent) | starter (Built-in Starter) | 9953 vs 3501 | **v1_main.py (Previous v1 Agent)** | +6452 | 2.44s |
| 6 | main.py (Current v2 Agent) | random (Built-in Random) | 8359 vs 0 | **main.py (Current v2 Agent)** | +8359 | 2.37s |

## Strategic Takeaways

- **`main.py (v2)` vs `v1_main.py (v1)`**: Tests land expansion timing and worker scaling optimizations.
- **Multi-Worker Advantage**: Utilizing farm hands ($1/day) significantly increases total crop harvests per day.
- **Land Expansion & End-Game Cutoff**: Expanding land and stopping late seed purchases boosts final score substantially.