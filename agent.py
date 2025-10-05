import argparse
from agent_logic.graph import build_graph

def main():
    """Main entry point to run the AI agent from the command line."""
    parser = argparse.ArgumentParser(description="Run the AI agent to generate a bank statement parser.")
    parser.add_argument("--target", type=str, required=True, help="The target bank name (e.g., 'icici').")
    args = parser.parse_args()
    
    target_bank = args.target
    print(f"--- Starting Agent for target: {target_bank} ---")

    # Assemble the agent's workflow from the graph definition
    app = build_graph()

    # Prepare the initial state for the agent's run
    initial_state = {
        "target_bank": target_bank,
        "pdf_path": f"data/{target_bank}/{target_bank}_sample.pdf",
        "csv_path": f"data/{target_bank}/{target_bank}_sample.csv",
        "attempts_left": 3,
        "error_history": []
    }

    # Invoke the agent and let it run
    final_state = app.invoke(initial_state)

# After the agent finishes, we print a clear final message.
print("\n--- Agent Run Finished ---")

# --- NEW CODE: Print the agent's plan ---
print("\n--- Agent's Final Plan ---")
print(final_state.get('plan', 'No plan generated.'))
# --- END NEW CODE ---

if final_state.get("test_output") == "Success":
    print("\n✅ Parser generated and tested successfully!")
    print(f"Final parser located at: custom_parsers/{target_bank}_parser.py")
else:
    print("\n❌ Agent failed to generate a working parser.")
    print("Final error:")
    print(final_state.get("error_history", ["No errors logged."])[-1])

if __name__ == "__main__":
    main()