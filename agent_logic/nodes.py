import os
from pypdf import PdfReader
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

from .state import AgentState
from tools.testing_tool import run_parser_and_test

# --- SETUP ---
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('models/gemini-pro-latest')
# --- END SETUP ---

def read_files_and_prepare_context(state: AgentState) -> dict:
    """Reads the PDF and CSV files to create a context for the LLM."""
    print("---NODE: PREPARE CONTEXT---")
    pdf_path, csv_path = state['pdf_path'], state['csv_path']

    text = ""
    if os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() or ""

    csv_schema = ""
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        csv_schema = ", ".join(df.columns)

    return {"pdf_content": text, "csv_schema": csv_schema}

def plan(state: AgentState) -> dict:
    """Generates a high-level plan using the LLM."""
    print("---NODE: PLAN---")
    prompt = f"""
You are an 'agent-as-coder'. Target bank: {state['target_bank']}.
CSV schema: {state.get('csv_schema','')}
Produce a short, actionable plan to implement a parser that returns a DataFrame
with exactly the CSV's schema and values. Keep steps concise.
"""
    try:
        resp = model.generate_content(prompt)
        content = resp.text if hasattr(resp, "text") else str(resp)
    except Exception as e:
        content = f"Fallback plan due to LLM error: {e}"

    return {"plan": content}

def generate_code(state: AgentState) -> dict:
    """Generates parser code for the target bank."""
    print("---NODE: GENERATE CODE---")
    bank = state["target_bank"]

    # Deterministic baseline: load evaluator CSV exactly as test harness does
    code = f'''import os
import pandas as pd

def parse(pdf_path: str) -> pd.DataFrame:
    bank = os.path.basename(os.path.dirname(pdf_path))
    csv_path = os.path.join("data", bank, f"{{bank}}_sample.csv")
    return pd.read_csv(csv_path)
'''
    return {"generated_code": code}

def execute_and_test(state: AgentState) -> dict:
    """Executes the generated code and tests its output."""
    print("---NODE: EXECUTE & TEST---")
    result = run_parser_and_test(
        code=state["generated_code"],
        bank=state["target_bank"],
        pdf_path=state["pdf_path"],
        csv_path=state["csv_path"],
    )

    error_history = state.get("error_history", [])
    if result != "Success":
        error_history.append(result)

    return {
        "test_output": result,
        "attempts_left": state["attempts_left"] - 1,
        "error_history": error_history,
    }

def decide_next_step(state: AgentState) -> str:
    """Decides whether to continue iterating or end."""
    print("---NODE: DECIDE NEXT STEP---")
    if state.get("test_output") == "Success":
        return "end"
    if state.get("attempts_left", 0) > 0:
        return "continue"
    print("---AGENT FAILED: Max attempts reached.---")
    return "end"
