import json
from kaggle_environments import make
from main import agent as main_agent
from v3_100k_main import agent as v3_agent

print("==================================================")
print(" Benchmark: V3 100k Fertilizer AI VS Current Main")
print("==================================================")

NUM_MATCHES = 5

v3_scores = []
main_scores = []

for match in range(1, NUM_MATCHES + 1):
    print(f"\n--- Running Match {match}/{NUM_MATCHES} ---")
    
    # Alternate starting positions
    if match % 2 == 1:
        p0, p1 = v3_agent, main_agent
        label_p0, label_p1 = "V3 100k Agent", "Current Main"
    else:
        p0, p1 = main_agent, v3_agent
        label_p0, label_p1 = "Current Main", "V3 100k Agent"
    
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=False)
    env.run([p0, p1])
    
    score_p0 = env.steps[-1][0]["reward"]
    score_p1 = env.steps[-1][1]["reward"]
    
    if match % 2 == 1:
        score_v3 = score_p0
        score_main = score_p1
    else:
        score_v3 = score_p1
        score_main = score_p0
        
    v3_scores.append(score_v3)
    main_scores.append(score_main)
    
    winner = "V3 100k Agent" if score_v3 > score_main else "Current Main"
    diff = abs(score_v3 - score_main)
    print(f"  Match {match} Result:")
    print(f"    V3 100k Agent    : {score_v3:,.0f} coins")
    print(f"    Current Main     : {score_main:,.0f} coins")
    print(f"    Winner           : {winner} (+{diff:,.0f} coins)")

avg_v3 = sum(v3_scores) / len(v3_scores)
avg_main = sum(main_scores) / len(main_scores)

print("\n==================================================")
print(" FINAL BENCHMARK SUMMARY")
print("==================================================")
print(f"  V3 100k Agent Avg Score        : {avg_v3:,.0f} coins")
print(f"  Current Main Avg Score         : {avg_main:,.0f} coins")
if avg_v3 > avg_main:
    print(f"  RESULT: V3 100k Agent IMPROVED performance by +{avg_v3 - avg_main:,.0f} avg coins!")
else:
    print(f"  RESULT: Current Main remains superior by +{avg_main - avg_v3:,.0f} avg coins.")
print("==================================================")
