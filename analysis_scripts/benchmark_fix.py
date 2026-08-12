import json
from kaggle_environments import make
from main import agent as main_agent
from fix_main import agent as fix_agent

print("==================================================")
print(" Benchmark: Fixed Agent (No Seed Cap) VS Current Main Agent")
print("==================================================")

NUM_MATCHES = 5

fix_scores = []
main_scores = []

for match in range(1, NUM_MATCHES + 1):
    print(f"\n--- Running Match {match}/{NUM_MATCHES} ---")
    
    # Alternate starting positions
    if match % 2 == 1:
        p0, p1 = fix_agent, main_agent
        label_p0, label_p1 = "Fixed Agent", "Current Main"
    else:
        p0, p1 = main_agent, fix_agent
        label_p0, label_p1 = "Current Main", "Fixed Agent"
    
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=False)
    env.run([p0, p1])
    
    score_p0 = env.steps[-1][0]["reward"]
    score_p1 = env.steps[-1][1]["reward"]
    
    if match % 2 == 1:
        score_fix = score_p0
        score_main = score_p1
    else:
        score_fix = score_p1
        score_main = score_p0
        
    fix_scores.append(score_fix)
    main_scores.append(score_main)
    
    winner = "Fixed Agent" if score_fix > score_main else "Current Main"
    diff = abs(score_fix - score_main)
    print(f"  Match {match} Result:")
    print(f"    Fixed Agent  : {score_fix:,.0f} coins")
    print(f"    Current Main : {score_main:,.0f} coins")
    print(f"    Winner       : {winner} (+{diff:,.0f} coins)")

avg_fix = sum(fix_scores) / len(fix_scores)
avg_main = sum(main_scores) / len(main_scores)

print("\n==================================================")
print(" FINAL BENCHMARK SUMMARY")
print("==================================================")
print(f"  Fixed Agent Average Score  : {avg_fix:,.0f} coins")
print(f"  Current Main Average Score : {avg_main:,.0f} coins")
if avg_fix > avg_main:
    print(f"  RESULT: Fixed Agent IMPROVED performance by +{avg_fix - avg_main:,.0f} avg coins! 🎉")
else:
    print(f"  RESULT: Current Main remains superior by +{avg_main - avg_fix:,.0f} avg coins.")
print("==================================================")
