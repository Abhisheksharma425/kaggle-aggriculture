import json
import glob

def analyze_replay(filepath):
    print(f"\n{'='*50}\nAnalyzing {filepath}\n{'='*50}")
    with open(filepath, "r") as f:
        replay = json.load(f)
        
    steps = replay["steps"]
    
    # Identify which agent is ours (ID 55451927). We can just check which one matches our logic, 
    # but we'll just track both and see which one expands land. Our agent usually gets 50k+ score.
    
    # We will pick the agent with the highest final score assuming that's our good bot, 
    # or just analyze both to be safe.
    agent_id = 0
    if steps[-1][1]["reward"] > steps[-1][0]["reward"]:
        agent_id = 1
        
    print(f"Tracking Agent {agent_id} (Final Score: {steps[-1][agent_id]['reward']})")
    
    days_seen = set()
    for step_idx, step_data in enumerate(steps):
        if not step_data or len(step_data) < 2:
            continue
            
        a0 = step_data[agent_id]
        obs = a0.get("observation", {})
        day = obs.get("day", 0)
        hour = obs.get("hour", 0)
        
        if day not in days_seen and hour == 23: # check at the end of the day
            days_seen.add(day)
            farm = obs.get("farms", [{}, {}])[agent_id]
            priv = obs.get("private", {})
            money = farm.get("money", 0)
            hands = len(farm.get("hands", []))
            quads = farm.get("unlocked_quadrants", [])
            tiles = farm.get("tiles", [])
            seeds = priv.get("seeds", {})
            
            # Quadrant usage
            quad_usage = {"NW": 0, "NE": 0, "SW": 0, "SE": 0}
            quad_total = {"NW": 25, "NE": 25, "SW": 25, "SE": 25}
            
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
            
            total_used = sum(quad_usage.values())
            unlocked_capacity = len(quads) * 25
            
            print(f"Day {day:2d} | Money: ${int(money):5d} | Hands: {hands} | Quads: {len(quads)} {quads}")
            print(f"   Usage: NW: {quad_usage['NW']}/25 | NE: {quad_usage['NE']}/25 | SW: {quad_usage['SW']}/25 | SE: {quad_usage['SE']}/25")
            print(f"   Total Used: {total_used} / {unlocked_capacity} capacity | Seeds: {sum(seeds.values())}")

for f in glob.glob("episode-*-replay.json"):
    analyze_replay(f)
