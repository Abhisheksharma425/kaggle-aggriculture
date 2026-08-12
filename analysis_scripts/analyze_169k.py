import json

with open('replays/episode-91924750-replay.json') as f:
    r = json.load(f)

steps = r['steps']
agent_id = 0
if steps[-1][1]['reward'] > steps[-1][0]['reward']: 
    agent_id = 1
    
print(f"Tracking Agent {agent_id} with score {steps[-1][agent_id]['reward']}")

for step_idx in range(len(steps)):
    s = steps[step_idx]
    if not s or len(s) < 2: continue
    
    obs = s[agent_id].get('observation', {})
    if not obs: continue
    day = obs.get('day', 0)
    hour = obs.get('hour', 0)
    
    if hour == 23 and day in [0, 5, 10, 15, 20, 25, 29]:
        me = obs.get('farms', [{}, {}])[agent_id]
        priv = obs.get('private', {})
        tiles = me.get('tiles', [])
        
        crops = {}
        animals = {}
        for y in range(10):
            for x in range(10):
                t = tiles[y][x]
                if isinstance(t, dict):
                    if t.get('kind') == 'PLANT':
                        c = t.get('crop')
                        crops[c] = crops.get(c, 0) + 1
                    elif t.get('kind') in ('PASTURE', 'COOP') and t.get('animal'):
                        a = t.get('animal')
                        animals[a] = animals.get(a, 0) + 1
        
        print(f"Day {day:2d} | Money: {me.get('money')} | Hands: {len(me.get('hands', []))}")
        print(f"         | Crops: {crops}")
        print(f"         | Animals: {animals}")
        # sum up quantities in shed
        shed_summary = {k: v for k, v in priv.get('shed', {}).items() if v > 0}
        print(f"         | Shed: {shed_summary}")
        print("-" * 60)
