"""
Script to run a local simulation of main.py against a baseline bot
and export an interactive visual simulation HTML file.
"""

import sys
from kaggle_environments import make
from main import agent as main_agent

def main():
    opponent = "starter"  # You can change to "random" or "pass"
    if len(sys.argv) > 1:
        opponent = sys.argv[1]

    print(f"Running simulation: main.py VS '{opponent}'...")
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
    env.run([main_agent, opponent])

    final = env.steps[-1]
    print("\n--- Match Finished ---")
    print(f"Player 0 (main.py): {final[0].reward:,.0f} coins ({final[0].status})")
    print(f"Player 1 ({opponent}): {final[1].reward:,.0f} coins ({final[1].status})")

    # Generate HTML visualization
    html_content = env.render(mode="html")
    output_filename = "simulation.html"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\nInteractive visual simulation saved to: {output_filename}")
    print("Open 'simulation.html' in your web browser (Chrome/Edge/Firefox) to watch the game playback!")

if __name__ == "__main__":
    main()
