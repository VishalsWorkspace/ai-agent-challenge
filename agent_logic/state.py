from typing import TypedDict, List

class AgentState(TypedDict):
    """
    Shared memory state of the agent across the graph.
    """
    target_bank: str
    pdf_path: str
    csv_path: str
    pdf_content: str
    csv_schema: str
    plan: str
    generated_code: str
    test_output: str
    error_history: List[str]
    attempts_left: int
