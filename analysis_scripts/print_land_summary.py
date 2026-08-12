import json

with open('land_analysis.json') as f:
    d = json.load(f)

for file, data in d.items():
    print(f"\n{'='*50}\n{file} | Final Score: {data['final_score']}\n{'='*50}")
    for x in data['days']:
        if x['day'] in [0, 5, 10, 15, 20, 25, 29]:
            print(f"Day {x['day']:2d} | Quads: {x['num_quads']} {x['quads']} | Hands: {x['hands']} | Seeds: {x['seeds']}")
            print(f"       | Usage: NW: {x['usage']['NW']}/25 | NE: {x['usage']['NE']}/25 | SW: {x['usage']['SW']}/25 | SE: {x['usage']['SE']}/25")
            print(f"       | Total Used: {sum(x['usage'].values())} / {x['num_quads'] * 25}")
