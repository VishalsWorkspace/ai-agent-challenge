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
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
            
    df = pd.read_csv(csv_path)
    csv_schema = ", ".join(df.columns)
    return {"pdf_content": text, "csv_schema": csv_schema}

def plan(state: AgentState) -> dict:
    """Generates a high-level plan using the LLM."""
    print("---NODE: PLAN---")
    prompt = f"""Create a plan to write a Python script that parses a bank statement PDF into a CSV.
    PDF Content Snippet: {state['pdf_content'][:2000]}
    Required CSV Schema: {state['csv_schema']}
    Provide a concise, step-by-step plan. Do not write code."""
    response = model.generate_content(prompt)
    return {"plan": response.text}

def generate_code(state: AgentState) -> dict:
    """Generates Python code based on the plan, context, and previous errors."""
    print("---NODE: GENERATE CODE---")
    error_history = "\n".join(state.get("error_history", []))
    prompt = f"""You are an expert Python programmer. Write a complete script with a single function `parse(pdf_path: str) -> pd.DataFrame`.
    
    **Plan:**
    {state['plan']}
    **PDF Content Snippet:**
    {state['pdf_content'][:2000]}
    **CSV Schema:**
    {state['csv_schema']}

    **Important Rules:**
    - Use `pypdf` and `pandas`.
    - The final DataFrame must match the schema: {state['csv_schema']}.

    **Previous Errors (Self-Correction):**
    ---
    {error_history}
    ---
    **Hint:** If the error is a `DataFrame shape mismatch`, your parsing logic is missing rows. Carefully re-examine the PDF text.

    Provide only the complete, runnable Python code.
    """
    response = model.generate_content(prompt)
    cleaned_code = response.text.replace("```python", "").replace("```", "").strip()
    return {"generated_code": cleaned_code}

def execute_and_test(state: AgentState) -> dict:
    """Executes the generated code and tests its output."""
    print("---NODE: EXECUTE & TEST---")
    result = run_parser_and_test(
        code=state["generated_code"],
        bank=state["target_bank"],
        pdf_path=state["pdf_path"],
        csv_path=state["csv_path"]
    )
    
    error_history = state.get("error_history", [])
    if result != "Success":
        error_history.append(result)

    return {
        "test_output": result,
        "attempts_left": state["attempts_left"] - 1,
        "error_history": error_history
    }

def decide_next_step(state: AgentState) -> str:
    """Determines the next step based on the test outcome."""
    print("---NODE: DECIDE NEXT STEP---")
    if state["test_output"] == "Success":
        return "end"
    elif state["attempts_left"] > 0:
        print(f"---TEST FAILED: {state['attempts_left']} attempts left. Retrying...---")
        return "continue"
    else:
        print("---AGENT FAILED: Max attempts reached.---")
        return "end"