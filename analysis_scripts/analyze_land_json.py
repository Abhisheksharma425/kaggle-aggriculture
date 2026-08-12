import json
import glob

results = {}

for filepath in glob.glob("episode-*-replay.json"):
    with open(filepath, "r") as f:
        replay = json.load(f)
        
    steps = replay["steps"]
    
    agent_id = 0
    if steps[-1][1]["reward"] > steps[-1][0]["reward"]:
        agent_id = 1
        
    ep_data = {
        "final_score": steps[-1][agent_id]['reward'],
        "days": []
    }
    
    days_seen = set()
    for step_idx, step_data in enumerate(steps):
        if not step_data or len(step_data) < 2:
            continue
            
        a0 = step_data[agent_id]
        obs = a0.get("observation", {})
        day = obs.get("day", 0)
        hour = obs.get("hour", 0)
        
        if day not in days_seen and hour == 23:
            days_seen.add(day)
            farm = obs.get("farms", [{}, {}])[agent_id]
            priv = obs.get("private", {})
            money = farm.get("money", 0)
            hands = len(farm.get("hands", []))
            quads = farm.get("unlocked_quadrants", [])
            tiles = farm.get("tiles", [])
            seeds = priv.get("seeds", {})
            
            quad_usage = {"NW": 0, "NE": 0, "SW": 0, "SE": 0}
            
            for y in range(10):
                for x in range(10):
                    q = ""
                    if x < 5 and y < 5: q = "NW"
                    elif x >= 5 and y < 5: q = "NE"
                    elif x < 5 and y >= 5: q = "SW"
                    else: q = "SE"
                    
                    t = tiles[y][x]
                    if isinstance(t, dict):
                        kind = t.get("kind")
                        if kind in ["PLANT", "PASTURE", "COOP"]:
                            quad_usage[q] += 1
            
            ep_data["days"].append({
                "day": day,
                "money": money,
                "hands": hands,
                "num_quads": len(quads),
                "quads": quads,
                "usage": quad_usage,
                "seeds": sum(seeds.values())
            })
            
    results[filepath] = ep_data

with open("land_analysis.json", "w") as f:
    json.dump(results, f, indent=2)
