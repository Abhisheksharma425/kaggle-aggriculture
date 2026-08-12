import json
with open('debug_v3.json') as f: r = json.load(f)
for s in r['steps']:
    if not s or len(s) < 2: continue
    obs0 = s[0].get('observation', {})
    if 'farms' not in obs0: continue
    if obs0['hour'] == 23 and obs0['day'] % 5 == 0:
        me = obs0['farms'][0]
        animals = 0
        for y in range(10):
            for x in range(10):
                t = me['tiles'][y][x]
                if isinstance(t, dict) and t.get('animal'): animals += 1
        shed_animals = obs0['private']['shed'].get('COW', 0) + obs0['private']['shed'].get('SHEEP', 0)
        print(f"Day {obs0['day']}: Animals on board {animals}, Animals in shed {shed_animals}")
