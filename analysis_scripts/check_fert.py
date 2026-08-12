import json
with open('debug_v3.json') as f: r = json.load(f)
for s in r['steps']:
    if not s or len(s) < 2: continue
    obs0 = s[0].get('observation', {})
    if 'farms' not in obs0: continue
    
    # check if any plant has fertilized_until_day
    for y in range(10):
        for x in range(10):
            t = obs0['farms'][0]['tiles'][y][x]
            if isinstance(t, dict) and t.get('kind') == 'PLANT' and t.get('fertilized_until_day', -1) > 0:
                print(f"Day {obs0['day']} Hour {obs0['hour']}: Plant at {x},{y} is fertilized until {t['fertilized_until_day']}")
                exit(0)
print('No plants were ever successfully fertilized.')
