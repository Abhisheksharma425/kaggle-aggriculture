# Baseline Rule-Based Strategy (Explained in Simple Terms)

## Overview

Our baseline agent currently scores **~9,700+ coins**, dominating the built-in starter agent (~3,500 coins) and random agent (0 coins). 

Instead of complicated artificial intelligence or machine learning, this agent works using **5 simple, logical rules** executed every single turn (720 turns = 30 days).

---

## The 5 Core Pillars of the Strategy

```
+-----------------------------------------------------------------------+
|                         EVERY TURN DECISION CYCLE                     |
+-----------------------------------------------------------------------+
|                                                                       |
|  1. MARKET ENGINE:                                                    |
|     - Sell all harvested crops in shed immediately.                   |
|     - Buy Wheat seeds (keep 10-15 seeds ready).                       |
|     - Hire 2-3 Farm Hands daily ($1 cost per hand).                   |
|     - Buy extra Land ($1,000) when bank > $2,000.                     |
|                                                                       |
|  2. WORKER PRIORITY QUEUE (Farmer + Hands):                            |
|     Priority 1: HARVEST mature Wheat (age >= 2 days) -> Cash in!      |
|     Priority 2: WATER thirsty plants -> Keep crops alive!             |
|     Priority 3: DIG weeds -> Clear blocked land!                      |
|     Priority 4: PLANT new Wheat seeds -> Keep soil active!            |
|                                                                       |
|  3. SMART NAVIGATION:                                                 |
|     - Workers calculate shortest grid distance to nearest task.       |
|     - Move 1 step (NORTH, SOUTH, EAST, WEST) directly toward task.   |
|                                                                       |
|  4. END-GAME SAVER:                                                   |
|     - On Day 28+, stop buying seeds & stop hiring hands.              |
|     - Pocket all coins for final game score!                          |
+-----------------------------------------------------------------------+
```

---

## 1. Market Engine: Automatic Cash Flow

Every single turn, the market processes orders automatically in the background:
- **Instant Selling**: Any crops sitting in your shed are instantly queued for `SELL`. This keeps money flowing into your bank.
- **Seed Buffer**: Maintains a reserve of 10 Wheat seeds (15 seeds once land expands). Seeds cost $10 each.
- **Cheap Labor**: Hires up to 2 farm hands daily (3 hands if land expanded).
  - *Why this works so well*: The first hand costs $1/day, the second hand costs $1/day. For just $2/day, you gain **48 extra actions every single day**!
- **Land Expansion**: Once bank savings reach $2,000, it buys the NE land quadrant for $1,000, doubling farm size from 25 to 50 tiles.

---

## 2. Worker Priority Queue: What to do First?

Every turn, all available workers (1 main farmer + hired hands) look at all unlocked farm tiles and choose actions based on strict priority:

1. **`HARVEST` (Priority 1)**: If standing on or near a wheat crop that is 2+ days old, harvest it immediately.
2. **`WATER` (Priority 2)**: If a crop hasn't been watered today, water it before doing anything else. If a plant isn't watered for 2 days, it turns into a weed!
3. **`DIG` (Priority 3)**: If a weed randomly spawns on empty land (0.5% chance per day), dig it out to free the tile.
4. **`PLANT` (Priority 4)**: If there is empty soil and we have Wheat seeds in stock, plant a seed.

---

## 3. Smart Navigation: Direct Grid Walking

Units don't wander around randomly.
- The agent calculates the **Manhattan distance** ($|x_1 - x_2| + |y_1 - y_2|$) between each worker and all unassigned task tiles.
- The worker picks the **closest task** and takes 1 step (`NORTH`, `SOUTH`, `EAST`, or `WEST`) directly toward that tile.
- When the worker arrives at the tile on the next turn, it performs the required task (`HARVEST`, `WATER`, `DIG`, or `PLANT`).

---

## 4. End-Game Savings Cutoff (Day 28 Strategy)

Wheat takes 2 days to grow. The season lasts 30 days (720 turns).
- If you buy a seed on Day 28 or 29, it will never finish growing before the game ends, wasting your money.
- **The Rule**: On Day 28, 29, and 30, the agent **completely stops buying seeds** and **stops hiring farm hands**.
- All money earned from final harvests stays safely in the bank, maximizing your final coin count.

---

## Summary of Results

| Agent | Final Money | Strategy Highlights |
| :--- | :--- | :--- |
| **Random Agent** | 0 coins | Random actions, moves into walls |
| **Built-in Starter** | ~3,500 coins | Simple 1-tile wheat loop, no movement, no hands |
| **Our Baseline Agent** | **~9,700+ coins** | Multi-tile farming, 3 workers, smart pathfinding, land expansion & end-game savings |
