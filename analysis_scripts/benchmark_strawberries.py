import json
from kaggle_environments import make
from main import agent as main_agent
from strawberry_main import agent as straw_agent

print("==================================================")
print(" Benchmark: Strawberry Agent VS Current Main Agent")
print("==================================================")

NUM_MATCHES = 5

straw_scores = []
main_scores = []

for match in range(1, NUM_MATCHES + 1):
    print(f"\n--- Running Match {match}/{NUM_MATCHES} ---")
    
    # Alternate starting positions
    if match % 2 == 1:
        p0, p1 = straw_agent, main_agent
        label_p0, label_p1 = "Strawberry Agent", "Current Main"
    else:
        p0, p1 = main_agent, straw_agent
        label_p0, label_p1 = "Current Main", "Strawberry Agent"
    
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=False)
    env.run([p0, p1])
    
    score_p0 = env.steps[-1][0]["reward"]
    score_p1 = env.steps[-1][1]["reward"]
    
    if match % 2 == 1:
        score_straw = score_p0
        score_main = score_p1
    else:
        score_straw = score_p1
        score_main = score_p0
        
    straw_scores.append(score_straw)
    main_scores.append(score_main)
    
    winner = "Strawberry Agent" if score_straw > score_main else "Current Main"
    diff = abs(score_straw - score_main)
    print(f"  Match {match} Result:")
    print(f"    Strawberry Agent : {score_straw:,.0f} coins")
    print(f"    Current Main     : {score_main:,.0f} coins")
    print(f"    Winner           : {winner} (+{diff:,.0f} coins)")

avg_straw = sum(straw_scores) / len(straw_scores)
avg_main = sum(main_scores) / len(main_scores)

print("\n==================================================")
print(" FINAL BENCHMARK SUMMARY")
print("==================================================")
print(f"  Strawberry Agent Average Score : {avg_straw:,.0f} coins")
print(f"  Current Main Average Score     : {avg_main:,.0f} coins")
if avg_straw > avg_main:
    print(f"  RESULT: Strawberry Agent IMPROVED performance by +{avg_straw - avg_main:,.0f} avg coins! 🎉")
else:
    print(f"  RESULT: Current Main remains superior by +{avg_main - avg_straw:,.0f} avg coins.")
print("==================================================")
