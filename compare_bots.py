import os
import json
from kaggle_environments import make
from main import agent as main_agent
from rank2_agent import agent as rank2_agent

print("==================================================")
print(" Head-to-Head Benchmark: Rank 2 Agent VS Current Main Agent")
print("==================================================")

NUM_MATCHES = 3

r2_scores = []
main_scores = []

for match in range(1, NUM_MATCHES + 1):
    print(f"\n--- Running Match {match}/{NUM_MATCHES} ---")
    
    # Game 1: Rank2 (Player 0) vs Main (Player 1)
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=False)
    env.run([rank2_agent, main_agent])
    
    score_r2 = env.steps[-1][0]["reward"]
    score_main = env.steps[-1][1]["reward"]
    
    r2_scores.append(score_r2)
    main_scores.append(score_main)
    
    winner = "Rank 2 Agent" if score_r2 > score_main else "Current Main Agent"
    diff = abs(score_r2 - score_main)
    print(f"  Match {match} Result:")
    print(f"    Rank 2 Agent  : {score_r2:,.0f} coins")
    print(f"    Current Main  : {score_main:,.0f} coins")
    print(f"    Winner        : {winner} (+{diff:,.0f} coins)")

avg_r2 = sum(r2_scores) / len(r2_scores)
avg_main = sum(main_scores) / len(main_scores)

print("\n==================================================")
print(" FINAL BENCHMARK SUMMARY")
print("==================================================")
print(f"  Rank 2 Agent Average Score : {avg_r2:,.0f} coins")
print(f"  Current Main Average Score : {avg_main:,.0f} coins")
if avg_r2 > avg_main:
    print(f"  Overall Winner             : Rank 2 Agent (+{avg_r2 - avg_main:,.0f} avg coins)")
else:
    print(f"  Overall Winner             : Current Main (+{avg_main - avg_r2:,.0f} avg coins)")
print("==================================================")

# Save result to JSON / Markdown score tracker
score_data = {
    "rank2_agent_avg": avg_r2,
    "current_main_avg": avg_main,
    "matches": [
        {"match": i + 1, "rank2": r2_scores[i], "main": main_scores[i]}
        for i in range(NUM_MATCHES)
    ]
}

with open("compare_scores.json", "w") as f:
    json.dump(score_data, f, indent=2)
