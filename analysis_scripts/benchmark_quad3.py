import json
from kaggle_environments import make
from main import agent as main_agent
from quad3_main import agent as quad3_agent

print("==================================================")
print(" Benchmark: Quad3 Agent VS Current Main Agent")
print("==================================================")

NUM_MATCHES = 5

quad3_scores = []
main_scores = []

for match in range(1, NUM_MATCHES + 1):
    print(f"\n--- Running Match {match}/{NUM_MATCHES} ---")
    
    # Alternate starting positions
    if match % 2 == 1:
        p0, p1 = quad3_agent, main_agent
        label_p0, label_p1 = "Quad3 Agent", "Current Main"
    else:
        p0, p1 = main_agent, quad3_agent
        label_p0, label_p1 = "Current Main", "Quad3 Agent"
    
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=False)
    env.run([p0, p1])
    
    score_p0 = env.steps[-1][0]["reward"]
    score_p1 = env.steps[-1][1]["reward"]
    
    if match % 2 == 1:
        score_quad3 = score_p0
        score_main = score_p1
    else:
        score_quad3 = score_p1
        score_main = score_p0
        
    quad3_scores.append(score_quad3)
    main_scores.append(score_main)
    
    winner = "Quad3 Agent" if score_quad3 > score_main else "Current Main"
    diff = abs(score_quad3 - score_main)
    print(f"  Match {match} Result:")
    print(f"    Quad3 Agent      : {score_quad3:,.0f} coins")
    print(f"    Current Main     : {score_main:,.0f} coins")
    print(f"    Winner           : {winner} (+{diff:,.0f} coins)")

avg_quad3 = sum(quad3_scores) / len(quad3_scores)
avg_main = sum(main_scores) / len(main_scores)

print("\n==================================================")
print(" FINAL BENCHMARK SUMMARY")
print("==================================================")
print(f"  Quad3 Agent Average Score      : {avg_quad3:,.0f} coins")
print(f"  Current Main Average Score     : {avg_main:,.0f} coins")
if avg_quad3 > avg_main:
    print(f"  RESULT: Quad3 Agent IMPROVED performance by +{avg_quad3 - avg_main:,.0f} avg coins!")
else:
    print(f"  RESULT: Current Main remains superior by +{avg_main - avg_quad3:,.0f} avg coins.")
print("==================================================")
