# Kaggriculture Bot Score Tracker

Last Updated: 2026-08-12

---

## 🏆 Head-to-Head Comparison: `rank2_agent.py` vs `main.py`

| Match | Rank 2 Agent (`rank2_agent.py`) | Current Main Bot (`main.py`) | Winner | Score Margin |
|---|---|---|---|---|
| **Match 1** | 14,425 coins | 51,054 coins | **Current Main** | +36,629 coins |
| **Match 2** | 17,636 coins | 62,342 coins | **Current Main** | +44,706 coins |
| **Match 3** | 15,625 coins | 53,027 coins | **Current Main** | +37,402 coins |
| **AVERAGE** | **15,895 coins** | **55,474 coins** | **Current Main** | **+39,579 coins** |

---

## 🔍 Key Findings & Insights

1. **Why `main.py` dominates (`55.4k` vs `15.8k`)**:
   * **Workforce Scaling Advantage**: `main.py` uses 7 hired farm hands. 8 units acting every turn can water, harvest, and feed across 50-100 tiles simultaneously.
   * **Single Farmer Bottleneck in `rank2_agent.py`**: Without hired hands, 1 single farmer gets overwhelmed trying to cover 100 tiles. Crops rot or go unwatered before the farmer can reach them.

2. **Best Takeaways to Merge into `main.py`**:
   * We can combine **Workforce Scaling** from `main.py` with **Day-0 Melon Launchpad & Ongoing Strawberries** from `rank2_agent.py` for an even higher score!

---

## 📁 File References
* **Rank 2 Strategy Agent**: [rank2_agent.py](file:///d:/Old%20laptop%20data/Python%20Haier/Python%20FIles/Kaggle%20Farm/rank2_agent.py)
* **Current Main Bot**: [main.py](file:///d:/Old%20laptop%20data/Python%20Haier/Python%20FIles/Kaggle%20Farm/main.py)
* **Comparison Script**: [compare_bots.py](file:///d:/Old%20laptop%20data/Python%20Haier/Python%20FIles/Kaggle%20Farm/compare_bots.py)