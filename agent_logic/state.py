from typing import TypedDict, List

class AgentState(TypedDict):
    """
    Represents the shared memory state of the agent as it moves through the graph.
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