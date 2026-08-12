import json
import os
import time
from kaggle_environments import make

# Import the agents
from main import agent as current_main_agent
from v1_main import agent as v1_main_agent
from new_main import agent as new_main_agent


def run_benchmark():
    print("=" * 65)
    print("KAGGAGRICULTURE BOT BENCHMARK FRAMEWORK - HEAD-TO-HEAD SHOWDOWN")
    print("=" * 65)

    competitors = {
        "main.py (Current v2 Agent)": current_main_agent,
        "v1_main.py (Previous v1 Agent)": v1_main_agent,
        "new_main.py (Single Farmer Baseline)": new_main_agent,
        "starter (Built-in Starter)": "starter",
        "random (Built-in Random)": "random",
    }

    matchups = [
        # Showdown 1: Current v2 vs Previous v1
        ("main.py (Current v2 Agent)", "v1_main.py (Previous v1 Agent)"),
        # Showdown 2: Current v2 vs Single Farmer Baseline
        ("main.py (Current v2 Agent)", "new_main.py (Single Farmer Baseline)"),
        # Showdown 3: Previous v1 vs Single Farmer Baseline
        ("v1_main.py (Previous v1 Agent)", "new_main.py (Single Farmer Baseline)"),
        # Showdown 4 & 5: vs Built-in Starter
        ("main.py (Current v2 Agent)", "starter (Built-in Starter)"),
        ("v1_main.py (Previous v1 Agent)", "starter (Built-in Starter)"),
        # Showdown 6: vs Built-in Random
        ("main.py (Current v2 Agent)", "random (Built-in Random)"),
    ]

    results = []

    for idx, (p1_name, p2_name) in enumerate(matchups, 1):
        print(f"\n[Match {idx}/{len(matchups)}] {p1_name}  VS  {p2_name}")
        env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=False)

        agent1 = competitors[p1_name]
        agent2 = competitors[p2_name]

        start_time = time.time()
        env.run([agent1, agent2])
        elapsed = time.time() - start_time

        final_step = env.steps[-1]
        p1_reward = final_step[0].get("reward", 0.0)
        p2_reward = final_step[1].get("reward", 0.0)

        if p1_reward > p2_reward:
            winner = p1_name
        elif p2_reward > p1_reward:
            winner = p2_name
        else:
            winner = "TIE"

        match_data = {
            "match_id": idx,
            "player_1": p1_name,
            "player_2": p2_name,
            "score_1": p1_reward,
            "score_2": p2_reward,
            "winner": winner,
            "margin": abs(p1_reward - p2_reward),
            "execution_time_sec": round(elapsed, 2),
        }
        results.append(match_data)

        print(f"   -> Result: {p1_name} ({p1_reward}) vs {p2_name} ({p2_reward}) | Winner: {winner}")

    # Save to JSON database
    json_file = "bot_scores.json"
    with open(json_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved raw benchmark data to {json_file}")

    # Generate Markdown Report
    md_file = "bot_scores.md"
    generate_markdown_report(results, md_file)
    print(f"Generated benchmark report in {md_file}")


def generate_markdown_report(results, filename):
    lines = [
        "# 🏆 Bot Benchmark & Score Tracker Report",
        "",
        "This file tracks and compares match performances across different bot strategies.",
        "",
        "## Matchup Results Overview",
        "",
        "| Match ID | Player 1 | Player 2 | Score (P1 vs P2) | Winner | Margin | Duration |",
        "| :---: | :--- | :--- | :---: | :--- | :---: | :---: |",
    ]

    for m in results:
        lines.append(
            f"| {m['match_id']} | {m['player_1']} | {m['player_2']} | {m['score_1']:.0f} vs {m['score_2']:.0f} | **{m['winner']}** | +{m['margin']:.0f} | {m['execution_time_sec']}s |"
        )

    lines.extend([
        "",
        "## Strategic Takeaways",
        "",
        "- **`main.py (v2)` vs `v1_main.py (v1)`**: Tests land expansion timing and worker scaling optimizations.",
        "- **Multi-Worker Advantage**: Utilizing farm hands ($1/day) significantly increases total crop harvests per day.",
        "- **Land Expansion & End-Game Cutoff**: Expanding land and stopping late seed purchases boosts final score substantially.",
    ])

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    run_benchmark()
