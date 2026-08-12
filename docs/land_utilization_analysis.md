# Land Utilization Analysis 

## The Problem
You noticed that our bot (`main.py`) purchases the 2nd and 3rd pieces of land in the late game, but we are unable to fully utilize them.

## Data Analysis
I analyzed recent Kaggle episodes (e.g., `92260597`, `92261510`, `91924750`) and tracked the exact number of tiles used per quadrant.

Here is what the data showed for a typical 55k-score game (`92260597`):
*   **Day 10:** 2 Quads unlocked (50 tiles capacity). We used exactly 27 tiles (NW: 25, NE: 2).
*   **Day 15:** 3 Quads unlocked (75 tiles capacity). We used exactly 37 tiles (NW: 25, NE: 7, SW: 5).
*   **Day 20:** 3 Quads unlocked. We used exactly 32 tiles. 
*   **Day 25:** 3 Quads unlocked. We used exactly 31 tiles.

Even though we paid $3,000 to unlock 50 additional tiles, **we never planted on more than ~12 of them at a time**. We consistently hovered around 31-37 total used tiles out of 75 available.

## The Root Causes

I dug into the code and simulated the agent's logic on the actual replay data. There are two major bugs in `main.py` causing this bottleneck:

### 1. The Hardcoded Seed Target Limit
In `main.py` at line 150, the seed purchasing logic is:
```python
plant_slots = len(empty_tiles) - needed_pastures
target_wheat_seeds = max(0, min(plant_slots, 12))  <--- BUG HERE
if wheat_seeds < target_wheat_seeds and money >= 10:
    buy_w = min(target_wheat_seeds - wheat_seeds, int(money // 10), 10)
    market.append(["BUY_SEED", "WHEAT", buy_w])
```
We hardcoded a cap of `12` for `target_wheat_seeds`!
When we unlock 3 quadrants, `plant_slots` becomes 75. But the code does `min(75, 12) = 12`. 
Because our target inventory is capped at 12 seeds, if we have 11 seeds in the shed, the bot buys exactly `1` seed. Our 7 hired workers can plant 7 seeds per turn, but they are starved of seeds because the market logic refuses to stockpile more than 12 seeds at any given time.

### 2. Market Order Prioritization
In the game, you can only execute a maximum of 10 market orders per turn.
Our order generation sequence is:
1.  **Sell items** (Milk, Wool, Fertilizer, etc.) -> takes ~4-5 slots.
2.  **Buy land** -> takes 0-1 slots.
3.  **Buy feed** -> takes 0-1 slots.
4.  **Buy animals** -> takes 0-1 slots.
5.  **Buy seeds** -> takes 1 slot.
6.  **Hire workers** -> takes up to 7 slots.

By the time we add 7 workers, our total market orders for the turn can hit 13-15. 
The code does `market = market[:10]` at the end, which slices off the bottom orders. Because worker hiring is at the very bottom, it gets truncated. But more importantly, because we can only ever buy a maximum of 10 seeds in a *single* order per turn, we mathematically cannot seed 75 tiles quickly enough if we are also constrained by the hardcoded limit of 12.

## How to Fix It
To actually utilize the 75-100 tiles we pay for, we need to:
1.  Remove the `12` seed cap. `target_wheat_seeds` should just be `plant_slots`.
2.  Allow the bot to buy seeds in bulk across multiple market orders if needed, or simply ensure we buy 10 seeds *every single turn* until we have enough to cover the entire farm.

If we fix this, our 7 workers will have enough seeds to plant the entire NE, SW, and SE quadrants, significantly boosting our late-game scoring!
