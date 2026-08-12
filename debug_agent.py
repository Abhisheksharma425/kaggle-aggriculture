from kaggle_environments import make
from main import agent

env = make("kaggriculture", configuration={"episodeSteps": 72}, debug=True)
env.run([agent, "pass"])

for step_idx in range(min(48, len(env.steps))):
    s = env.steps[step_idx][0]
    obs = s.get("observation", {})
    act = s.get("action", {})
    me = obs["farms"][0]
    priv = obs["private"]
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)
    money = me["money"]
    hands = len(me.get("hands", []))
    shed_items = {k: v for k, v in priv["shed"].items() if v > 0}
    invs = priv.get("inventories", [{}])
    inv0 = {k: v for k, v in invs[0].items() if v > 0} if invs else {}
    market_acts = act.get("market", [])
    farmer_act = act.get("farmer", [])
    hands_acts = act.get("hands", [])
    print(
        "S", step_idx,
        "D" + str(day), "H" + str(hour),
        "$" + str(int(money)),
        "H:" + str(hands),
        "Shed:", shed_items,
        "Inv0:", inv0,
        "F:", farmer_act,
        "Hands:", hands_acts[:3],
        "M:", market_acts[:4],
    )

print()
print("Final money:", int(env.steps[-1][0]["observation"]["farms"][0]["money"]))
