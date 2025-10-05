from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import read_files_and_prepare_context, plan, generate_code, execute_and_test, decide_next_step

def build_graph():
    """Builds the agent's workflow as a state machine."""
    workflow = StateGraph(AgentState)

    workflow.add_node("read_files", read_files_and_prepare_context)
    workflow.add_node("plan", plan)
    workflow.add_node("generate_code", generate_code)
    workflow.add_node("execute_and_test", execute_and_test)

    workflow.set_entry_point("read_files")

    workflow.add_edge("read_files", "plan")
    workflow.add_edge("plan", "generate_code")
    workflow.add_edge("generate_code", "execute_and_test")
    
    workflow.add_conditional_edges(
        "execute_and_test",
        decide_next_step,
        {"continue": "generate_code", "end": END}
    )

    app = workflow.compile()
    return app