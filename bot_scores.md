# 🏆 Bot Benchmark & Score Tracker Report

This file tracks and compares match performances across different bot strategies.

## Matchup Results Overview

| Match ID | Player 1 | Player 2 | Score (P1 vs P2) | Winner | Margin | Duration |
| :---: | :--- | :--- | :---: | :--- | :---: | :---: |
| 1 | main.py (Our Optimized Agent) | new_main.py (Single Farmer Baseline) | 9169 vs 2670 | **main.py (Our Optimized Agent)** | +6499 | 2.07s |
| 2 | main.py (Our Optimized Agent) | starter (Built-in Starter) | 9953 vs 3487 | **main.py (Our Optimized Agent)** | +6466 | 2.07s |
| 3 | new_main.py (Single Farmer Baseline) | starter (Built-in Starter) | 2670 vs 3487 | **starter (Built-in Starter)** | +817 | 1.3s |
| 4 | main.py (Our Optimized Agent) | random (Built-in Random) | 8605 vs 0 | **main.py (Our Optimized Agent)** | +8605 | 2.09s |
| 5 | new_main.py (Single Farmer Baseline) | random (Built-in Random) | 2670 vs 0 | **new_main.py (Single Farmer Baseline)** | +2670 | 1.29s |

## Analysis & Takeaways

- **`main.py` vs `new_main.py`**: Compares multi-worker + land expansion strategy against single-farmer baseline.
- **Multi-Worker Advantage**: Utilizing farm hands ($1/day) significantly increases total crop harvests per day.
- **Land Expansion & End-Game Cutoff**: Expanding land and stopping late seed purchases boosts final score substantially.