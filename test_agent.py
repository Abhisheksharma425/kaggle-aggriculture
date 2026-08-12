import json
import os
import webbrowser
from kaggle_environments import make
from main import agent


def run_test():
    print("Initializing environment...")
    # Create the kaggriculture environment with 720 turns (30 days)
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)

    print("Running simulation (main.py vs starter)...")
    # Run our agent against the built-in starter agent
    env.run([agent, "starter"])

    # Get the final results
    final = env.steps[-1]
    print("\n--- Match Results ---")
    for i, s in enumerate(final):
        reward = s.get("reward", 0)
        status = s.get("status", "UNKNOWN")
        name = "Our Agent" if i == 0 else "Starter Agent"
        print(f"Player {i} ({name}): reward={reward}, status={status}")

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
    print("Opening simulation visualizer in web browser...")
    webbrowser.open("file://" + os.path.abspath(html_path))


if __name__ == "__main__":
    run_test()
