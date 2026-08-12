import json
import main

# redefine agent locally with prints
with open('main.py', 'r') as f:
    code = f.read()

code = code.replace(
    'market.append(["BUY_SEED", "WHEAT", buy_w])', 
    'print(f"BUY_W: {buy_w}, avail: {available_slots}, empty: {len(empty_tiles)}, seeds: {wheat_seeds}, money: {money}, weed_count: {len(weeds)}"); market.append(["BUY_SEED", "WHEAT", buy_w])'
)

with open('temp_main.py', 'w') as f:
    f.write(code)

import temp_main

with open('episode-92260597-replay.json') as f: 
    r = json.load(f)

for s in r['steps']:
    obs = s[0]['observation']
    if obs['day'] == 15 and obs['hour'] == 23:
        act = temp_main.agent(obs)
        break
