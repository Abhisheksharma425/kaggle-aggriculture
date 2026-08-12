import json

with open("episode-91940849-replay.json", "r") as f:
    replay = json.load(f)

steps = replay["steps"]
final_step = steps[-1]

print("=== FINAL SCORES ===")
for i, s in enumerate(final_step):
    print(f"Agent {i}: reward = {s.get('reward')}")

print("\n=== AGENT 0 (KAWASHIGE / RANK 2) TIMELINE ===")
# Trace key milestones over days
days_seen = set()
for step_idx, step_data in enumerate(steps):
    if not step_data or len(step_data) < 2:
        continue

    # Let's inspect Agent 0 and Agent 1
    # Check step 1 action format to know which one is Kawashige
    a0 = step_data[0]
    obs0 = a0.get("observation", {})
    day = obs0.get("day", 0)
    hour = obs0.get("hour", 0)

    if day not in days_seen and hour == 0:
        days_seen.add(day)
        farm0 = obs0.get("farms", [{}, {}])[0]
        priv0 = obs0.get("private", {})
        money = farm0.get("money", 0)
        hands = len(farm0.get("hands", []))
        quads = farm0.get("unlocked_quadrants", [])
        shed = priv0.get("shed", {})
        seeds = priv0.get("seeds", {})
        tiles = farm0.get("tiles", [])

        # Count plants, pastures, animals
        cows = 0
        sheep = 0
        pastures = 0
        wheat_plants = 0
        straw_plants = 0
        melon_plants = 0

        for row in tiles:
            for cell in row:
                if isinstance(cell, dict):
                    k = cell.get("kind")
                    if k == "PASTURE":
                        pastures += 1
                        anim = cell.get("animal")
                        if anim == "COW": cows += 1
                        elif anim == "SHEEP": sheep += 1
                    elif k == "PLANT":
                        crop = cell.get("crop")
                        if crop == "WHEAT": wheat_plants += 1
                        elif crop == "STRAWBERRY": straw_plants += 1
                        elif crop == "MELON": melon_plants += 1

        act0 = a0.get("action", {})
        market_acts = act0.get("market", [])

        print(f"Day {day:2d} | Money: ${int(money):6d} | Hands: {hands:2d} | Quads: {quads} | Pastures: {pastures} (Cows:{cows}, Sheep:{sheep}) | Crops: Wheat:{wheat_plants}, Straw:{straw_plants}, Melon:{melon_plants} | Market: {market_acts[:3]}")
