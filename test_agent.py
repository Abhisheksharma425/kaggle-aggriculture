import json
import os
import webbrowser
from kaggle_environments import make

from main import agent as main_agent
from v1_main import agent as v1_agent


def run_test():
    print("Initializing environment...")
    # Create the kaggriculture environment with 720 turns (30 days)
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)

    print("\n==================================================")
    print(" Running Simulation: New Bot (main.py) VS Previous Bot (v1_main.py)")
    print("==================================================\n")

    # Run New Bot (main.py) vs Previous Bot (v1_main.py)
    env.run([main_agent, v1_agent])

    # Get the final results
    final = env.steps[-1]
    print("\n--- Final Match Results ---")
    score_p0 = final[0].get("reward", 0)
    score_p1 = final[1].get("reward", 0)

    print(f"  Player 0 (New Bot - main.py)      : {score_p0} coins")
    print(f"  Player 1 (Previous Bot - v1_main.py): {score_p1} coins")

    if score_p0 > score_p1:
        print(f"\n  WINNER: New Bot (main.py) by +{score_p0 - score_p1} coins!")
    elif score_p1 > score_p0:
        print(f"\n  WINNER: Previous Bot (v1_main.py) by +{score_p1 - score_p0} coins!")
    else:
        print("\n  TIE MATCH!")

    # 1. Save JSON replay file
    replay_json_path = "replay.json"
    print(f"\nSaving replay JSON to {replay_json_path}...")
    with open(replay_json_path, "w") as f:
        json.dump(env.toJSON(), f)
    print("Replay JSON saved successfully!")

    # 2. Render and save HTML simulation visualizer
    print("\nRendering HTML simulation visualizer...")
    html_content = env.render(mode="html", width=800, height=800)

    html_path = "replay.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Saved simulation HTML to {os.path.abspath(html_path)}")

    # 3. Open in browser automatically
    print("\nOpening interactive simulation visualizer in web browser...")
    webbrowser.open("file://" + os.path.abspath(html_path))


if __name__ == "__main__":
    run_test()
