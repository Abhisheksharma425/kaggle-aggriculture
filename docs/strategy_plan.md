# Kaggriculture Agent Strategy & System Architecture Plan

## Executive Summary

This document presents a comprehensive analysis, system architecture, and strategic roadmap for building a top-tier competitive agent for Kaggle's **Kaggriculture** environment.

The solution is structured in a **modular, layered architecture**:
1. **Layer 0 (Foundation)**: Game state parser, grid representation, simulation engine, pathfinding (BFS/A*), and market price simulator.
2. **Layer 1 (Baseline Rule-Based Agent)**: A deterministic, highly-optimized rule-based state machine handling task assignment, plant/animal lifecycle, hiring economics, inventory management, and market trading.
3. **Layer 2 (Heuristic Optimization & Market Arbitrage)**: Dynamic crop selection based on expected Return-on-Investment (ROI), town demand tracking, market glut avoidance, and multi-hand spatial task allocation.
4. **Layer 3 (Advanced AI / Search / RL)**: Model Predictive Control (MPC), Tree Search (MCTS/Minimax), or Reinforcement Learning built seamlessly on top of Layer 0-2 abstractions.

---

## 1. Comprehensive Game Mechanics & Economic Analysis

### 1.1 Economic Profiles of Crops & Animals

| Item | Seed Cost | Base Price | Yield Time | Daily Yield/Tile | Shape Above $I_0$ | Risk Level | Primary Role |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Wheat** | $10 | $25 | 2–4 days | 0.80 | `log` (resilient) | Low | Early capital boost, animal feed |
| **Carrot** | $20 | $35 | 2–3 days | 0.75 | `sqrt` (moderate) | Low-Med | Fast cash cycle |
| **Tomato** | $50 | $60 | 8–11 days | 0.33 | `sqrt` (moderate) | Medium | Steady ongoing passive income |
| **Strawberry** | $100 | $120 | 10–16 days | 0.24 | `linear` (fragile) | High | Mid-late high value shop demand |
| **Melon** | $80 | $250 | 10 days | 0.55 | `sq` (extreme fragility) | High | Massive burst profit, fragile market |
| **Goose (Egg)** | $300 | $50 | 4 days | 1.00 | `log` (resilient) | Low-Med | Daily steady income + fertilizer |
| **Cow (Milk)** | $400 | $160 | 8 days | 0.50 | `linear` (fragile) | Med-High | Premium mid-game livestock |
| **Sheep (Wool)**| $500 | $200 | 6 days | 0.33 | `sq` (extreme fragility) | High | Highest base price, needs Yarn Store |

### 1.2 Key Strategic Insights

1. **Market Price Sensitivity & Dynamic Glut Avoidance**:
   - Selling high-tier products (Melon, Wool, Milk, Strawberry) into a saturated market ($I > I_0$) collapses prices rapidly down to the $1 floor due to quadratic (`sq`) or linear price shape functions.
   - **Rule**: Never flood the market with Melon/Wool/Strawberry all at once. Stagger sales or time them with town building demand spikes!

2. **Town Center & Shop Demand Arbitrage**:
   - Town buildings consume products from the market for free:
     - Town center drains 1 of each product every 12 turns (2x after day 10, 4x after day 20).
     - New shops unlock every 3 days and consume demanded items every 4 turns.
   - Town consumption drives market inventory below $I_0$, causing prices to surge above base value (e.g. Melon price rising to $300+).
   - **Rule**: Monitor `obs["town"]["unlocked_shops"]` dynamically and prioritize planting crops / raising animals demanded by active shops.

3. **Farm Hand Scaling Economics**:
   - Hiring cost follows Fibonacci sequence: $1, 1, 2, 3, 5, 8, 13, 21, \dots$ daily.
   - 1st & 2nd hands cost only $1 each (2 extra actions/turn for 24 turns = 48 action steps for just $2/day!).
   - **Rule**: Always hire at least 2 farm hands per day once daily income exceeds ~$50. Hire 3-4 hands when managing large expanded farms.

4. **Land Expansion Timing**:
   - Quadrant costs: NW ($0, starting), NE ($1,000), SW ($2,000), SE ($4,000).
   - Expanding land increases farm area from 25 to 50, 75, and 100 tiles.
   - **Rule**: Only buy NE quadrant when NW quadrant is >80% utilized and bank balance > $1,500.

5. **Watering & Fertilizer Synergy**:
   - One-time crops (Wheat, Carrot, Melon): Fertilizing doubles the bonus watering window yield (+2 yield/day instead of +1).
   - Ongoing crops (Tomato, Strawberry): Watering + Fertilizing doubles scheduled production yield (2 units instead of 1).
   - Fertilizer collected from animals (`COLLECT_FERTILIZER`) saves $100 market purchase cost.

---

## 2. System Architecture & Module Design

```
+-------------------------------------------------------------------+
|                        Kaggriculture Agent                        |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                      1. Game State & Knowledge                    |
|   - Board Grid State (Tiles, Shed, Units, Watered/Fed flags)      |
|   - Market Tracker (Prices, Supply trends, Shape functions)       |
|   - Town Demand Engine (Shop unlock prediction & demand rates)    |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                    2. Action Planner & Task Queue                 |
|   - Task Generator (Plant, Water, Harvest, Feed, Care, Dig)       |
|   - Spatial Pathfinding & Distance Matrix (BFS / A*)              |
|   - Hand Assignment Optimizer (Hungarian Algorithm / Greedy)      |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                    3. Market & Economic Controller                |
|   - Seed / Animal Purchase Manager                                |
|   - Optimal Order Queuing & Batch Selling                         |
|   - Farm Hand Hiring Budgeting                                    |
+-------------------------------------------------------------------+
```

### 2.1 Proposed Code Directory Structure

```
kaggle_farm/
│── main.py                     # Entry point containing agent(obs) function
│── strategy_plan.md            # Detailed strategy document
│── src/
│   │── __init__.py
│   │── state.py                # Game state parser and tile grid wrapper
│   │── pathfinding.py          # Grid navigation, shortest paths, BFS
│   │── market.py               # Market price modeling & order queue builder
│   │── tasks.py                # Task representation (HARVEST, WATER, PLANT, etc.)
│   │── scheduler.py            # Multi-unit task scheduler (Farmer + Hands)
│   └── strategies/
│       │── __init__.py
│       │── base_strategy.py    # Abstract strategy class
│       │── baseline_rule.py    # Robust deterministic rule-based strategy
│       └── dynamic_roi.py      # Dynamic ROI & Arbitrage strategy
└── tests/
    │── test_rules.py           # Unit tests for rule engine
    └── test_simulation.py      # Environment match runner
```

---

## 3. Solution Approaches (Detailed Exploration)

### Solution 1: Baseline Rule-Based Strategy (Phase 1 Target)
* **Concept**: Deterministic state machine managing 1 Farmer on NW quadrant (25 tiles).
* **Crop Cycle**: Focus on Wheat & Carrot loops.
* **Behavior**:
  - Maintain 10-15 Wheat/Carrot tiles.
  - Prioritize tasks: `HARVEST` > `WATER` > `PLANT` > `DIG` weed.
  - Market: Buy seeds when count = 0; Sell produce immediately if market price $\ge \text{base}$.
  - Hire 1-2 hands daily to help water and plant.
* **Pros**: Low complexity, 100% reliable, zero unexpected crashes.
* **Expected Score**: ~3,000 - 8,000 coins.

### Solution 2: Multi-Crop Dynamic ROI Arbitrage Strategy
* **Concept**: Dynamically calculates the expected profit per tile-day for each crop/animal option.
  $$\text{ROI}_c = \frac{\text{Expected Sales Price} \times \text{Yield} - \text{Seed Cost}}{\text{Growth Days} \times \text{Labor Turns}}$$
* **Behavior**:
  - Shifts planting plan towards Wheat when market wheat price is high, Carrot for quick turns, Melon when town shop demand drains melon inventory.
  - Prevents market price collapse by capping single-turn sales to $N$ units.
* **Pros**: Maximizes profit margins across shifting market conditions.

### Solution 3: Integrated Farm & Livestock Loop
* **Concept**: Combines crop farming with livestock (Goose/Cow/Sheep).
* **Behavior**:
  - Wheat tiles feed animals daily.
  - Goose/Cow yield high-value products (Egg/Milk).
  - Collect fertilizer to boost high-yield crops (Melon/Strawberry).
* **Pros**: High long-term steady daily payout.
* **Cons**: Requires strict daily feeding loop; missing 2 days loses livestock.

### Solution 4: Multi-Hand Spatial Scheduler (Hungarian Matching + BFS)
* **Concept**: Treats task allocation for Farmer + $K$ hands as a bipartite matching problem.
* **Behavior**:
  - Compute shortest Manhattan / pathfinding distance from each unit to all pending tasks.
  - Assign closest unit to critical tasks (`WATER`, `FEED`, `HARVEST`).
* **Pros**: Eliminates wasted movement turns, maximizing action density per day.

---

## 4. Phased Implementation Roadmap

1. **Phase 1: Project Restructuring & Core Baseline Agent (Immediate)**
   - Modularize codebase into `src/` directory.
   - Implement `state.py`, `pathfinding.py`, `tasks.py`, `scheduler.py`, and `baseline_rule.py`.
   - Validate with local simulation runs against `"random"` and `"starter"` baseline agents.

2. **Phase 2: Town & Market Arbitrage Engine**
   - Implement `market.py` to calculate exact dynamic price impact before selling.
   - Track town shop unlocks and adjust crop selection.

3. **Phase 3: Multi-Hand Spatial Navigation & Task Scheduler**
   - Implement distance-aware task queueing for Farmer + 2-4 Hired Hands.
   - Optimize shed drop-offs and inventory management.

4. **Phase 4: Optimization & Advanced AI Layer**
   - Perform hyperparameter tuning on economic thresholds (hire limits, selling batch sizes).
   - (Optional) Build Monte Carlo Tree Search (MCTS) or Reinforcement Learning agent using the modular environment abstractions.

---

## 5. Verification & Testing Plan

1. **Unit Tests**:
   - Action generator correctness (ensure no illegal moves or invalid market orders).
   - Pathfinding correctness (avoid locked tile action attempts).
2. **Local Simulation Benchmark**:
   - Run 100 episodes against `starter` and `random` baselines.
   - Target: >95% win rate and final reward > 15,000 coins.
3. **Kaggle Environment Submission Validation**:
   - Test single-file vs multi-file tar.gz submission format using `kaggle-environments`.
