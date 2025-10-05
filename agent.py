import argparse
import traceback
from agent_logic.graph import build_graph

def main():
    parser = argparse.ArgumentParser(description="Run the AI agent to generate a bank statement parser.")
    parser.add_argument("--target", type=str, required=True, help="The target bank name (e.g., 'icici').")
    args = parser.parse_args()

    target_bank = args.target
    print(f"--- Starting Agent for target: {target_bank} ---")

    app = build_graph()

    initial_state = {
        "target_bank": target_bank,
        "pdf_path": f"data/{target_bank}/{target_bank}_sample.pdf",
        "csv_path": f"data/{target_bank}/{target_bank}_sample.csv",
        "attempts_left": 3,
        "error_history": [],
    }

    final_state = {}
    try:
        final_state = app.invoke(initial_state)
    except Exception as e:
        print("\n--- AGENT INVOCATION FAILED ---")
        print(f"ERROR: {e}")
        print("\n--- FULL TRACEBACK ---")
        traceback.print_exc()
        return

    print("\n--- Agent Run Finished ---")
    print("\n--- Agent's Final Plan ---")
    print(final_state.get("plan", "No plan generated."))

    if final_state.get("test_output") == "Success":
        print("\n✅ Parser generated and tested successfully!")
        print(f"Final parser located at: custom_parsers/{target_bank}_parser.py")
    else:
        print("\n❌ Agent failed to generate a working parser.")
        errors = final_state.get("error_history", [])
        if errors:
            print("Final error:\n" + errors[-1])
        else:
            print("No specific errors were logged by the agent.")

if __name__ == "__main__":
    main()
