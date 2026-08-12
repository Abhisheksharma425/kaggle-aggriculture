import json
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
        print(f"Player {i} ({'Our Agent' if i == 0 else 'Random Agent'}): reward={reward}, status={status}")
    
    # Save the replay file for debugging/visualization
    replay_path = "replay.json"
    print(f"\nSaving replay to {replay_path}...")
    with open(replay_path, "w") as f:
        json.dump(env.toJSON(), f)
    print("Replay saved successfully!")

if __name__ == "__main__":
    run_test()
