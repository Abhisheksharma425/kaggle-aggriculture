# How Our Kaggriculture Bot Works (In Simple Terms)

Our bot uses a high-performance **"Cash Engine + High-Yield Livestock"** strategy designed to maximize income over 30 in-game days (720 turns).

---

## 💡 The Core Idea

Instead of spending all money upfront on slow, expensive crops, our bot acts like a smart business:
1. **Fast Cash Engine**: Uses Wheat (fast 2-day harvest) to build cash quickly.
2. **High-Value Assets**: Reinvests profits into Cows (Milk) and Sheep (Wool) for massive daily profits.
3. **Automated Supply Chain**: Hires workers to automatically carry feed, water crops, harvest products, and sell goods at the market.

---

## 🚜 How the Bot Operates (Phase by Phase)

### Phase 1: Building the Engine (Days 0 – 4)
* **Plant Wheat Everywhere**: Wheat seeds only cost $10 and mature in just 2 days.
* **Daily Harvest Cycle**: Workers water crops, harvest mature wheat, and sell it immediately.
* **Bankroll Growth**: Turns starting cash ($3,000) into a steady stream of revenue.

---

### Phase 2: Expanding Livestock & Feeding Pipeline (Days 4 – 20)
* **Building Pastures**: Converts empty farm tiles into animal pastures.
* **Buying Cows & Sheep**: Adds Cows (Milk sells for ~$160) and Sheep (Wool sells for ~$200).
* **The 4-Step Feeding Pipeline**:
  1. **Pickup Feed**: Worker walks to the shed and picks up Wheat into their inventory.
  2. **Feed Animal**: Worker walks to the pasture tile and feeds the animal.
  3. **Care Bonus**: Worker gives extra `CARE` to animals to increase daily milk/wool output.
  4. **Harvest & Drop**: Worker collects Milk, Wool, and Fertilizer, carrying them back to drop at the shed.

---

### Phase 3: Scaling Workers & Unlocking Land (Days 6 – 28)
* **Smart Worker Hiring**: Every day, the bot hires up to 7 farm hands. Hire costs grow as `$1, $1, $2, $3, $5, $8, $13...` so it stops before overspending.
* **Land Expansion**: Unlocks new land quadrants (NE at Day 8 for $1,000, SW at Day 14 for $2,000) once cash reserves are high.
* **Feed Arbitrage**: If the farm runs low on wheat feed, the market manager automatically buys extra Wheat from the market for $25/unit to keep animals fed and producing.

---

### Phase 4: Harvest & Market Automation (Every Turn)
* **Automated Selling**: Market orders run every single turn, instantly converting stored Milk, Wool, Fertilizer, and surplus Wheat into bank cash.
* **End-Game Freeze (Days 28–30)**: Stops buying expensive assets or hiring new workers in the last 2 days, saving all money directly in the bank to maximize the final score.

---

## 📊 Performance Comparison

| Strategy Version | Avg Final Score | Main Feature |
|---|---|---|
| **v1 Bot** | ~8,500 coins | Simple Wheat loop |
| **New Bot (Current)** | **~57,500 coins** | **Wheat Engine + Livestock Pipeline + Smart Hiring** |

---

## 📁 Key File Locations
* **Bot Implementation**: [main.py](file:///d:/Old%20laptop%20data/Python%20Haier/Python%20FIles/Kaggle%20Farm/main.py)
* **Local Simulation Harness**: [test_agent.py](file:///d:/Old%20laptop%20data/Python%20Haier/Python%20FIles/Kaggle%20Farm/test_agent.py)
* **HTML Simulation Visualizer**: [replay.html](file:///d:/Old%20laptop%20data/Python%20Haier/Python%20FIles/Kaggle%20Farm/replay.html)
