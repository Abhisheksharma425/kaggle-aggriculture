import json
with open('debug_v3.json') as f: r = json.load(f)
for s in r['steps']:
    if not s or len(s) < 2: continue
    obs0 = s[0].get('observation', {})
    if 'farms' not in obs0: continue
    if obs0['hour'] == 23 and obs0['day'] % 5 == 0:
        money = obs0['farms'][0]['money']
        shed = obs0['private']['shed']
        shed_fert = shed.get('FERTILIZER', 0)
        hands = len(obs0['farms'][0].get('hands', []))
        # Count crops
        crops = {'WHEAT': 0, 'MELON': 0, 'STRAWBERRY': 0}
        for y in range(10):
            for x in range(10):
                t = obs0['farms'][0]['tiles'][y][x]
                if isinstance(t, dict) and t.get('kind') == 'PLANT':
                    c = t.get('crop', 'WHEAT')
                    if c in crops: crops[c] += 1
                    
        print(f"Day {obs0['day']:2d} | Money: {money:7.0f} | Hands: {hands:2d} | Shed Fert: {shed_fert:2d} | Crops: {crops}")
