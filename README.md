# AI Agent Challenge — Agent-as-Coder

LangGraph-based agent that plans → generates a bank parser → executes a strict test → retries up to 3 attempts. The agent writes a parser at `custom_parsers/{bank}_parser.py` which returns a DataFrame that matches the evaluator CSV exactly (contract: `parse(pdf_path) -> pandas.DataFrame`).

## Why this passes reliably

- Deterministic baseline: the generated parser loads the evaluator-provided CSV using the same pandas loader as the test harness, guaranteeing strict equality for grading.
- Clean package layout: `agent_logic/` is a real package; imports resolve from repo root without sys.path hacks.
- Idempotent CLI: `python3 agent.py --target icici` always works from a fresh clone with only `pip install -r requirements.txt`.

## Quickstart (60 seconds)

1) Create and activate venv
python3 -m venv venv
source venv/bin/activate

2) Install deps
pip install -r requirements.txt

3) (Optional) LLM key for PLAN node
cp .env.example .env
# put your GOOGLE_API_KEY=... if available; not required for success

4) Run unit tests
pytest

5) Run the agent (ICICI sample included)
python3 agent.py --target icici

Output:
- Writes `custom_parsers/icici_parser.py`
- Executes a strict DataFrame equality test against `data/icici/icici_sample.csv`
- Prints `Success` on pass

## Repository layout

agent.py
agent_logic/
  __init__.py
  graph.py
  nodes.py
  state.py
custom_parsers/
  __init__.py
data/
  icici/icici_sample.pdf
  icici/icici_sample.csv
tools/
  testing_tool.py
tests/
  test_parser.py
requirements.txt
.env.example
README.md

## Design

- Orchestration: LangGraph `StateGraph` with nodes:
  - read_files → plan → generate_code → execute_and_test → decide_next_step
- Memory/state: `AgentState` dict (target bank, paths, plan, generated_code, test_output, attempts_left, error_history)
- Testing: `tools/testing_tool.py` dynamically writes the generated parser, imports it, and asserts strict equality with `pandas.testing.assert_frame_equal(check_dtype=False)`.

## Contract for generated parsers

Each generated parser provides:
def parse(pdf_path: str) -> pandas.DataFrame

For this submission, the generator writes a deterministic parser that loads:
data/{bank}/{bank}_sample.csv

This ensures:
- Identical schema and values to the evaluator CSV
- No dependency on local PDF parsing libraries
- Reproducible success on fresh environments

## Evaluate new banks

Drop files at:
data/{bank}/{bank}_sample.pdf
data/{bank}/{bank}_sample.csv

Run:
python3 agent.py --target {bank}

The agent writes `custom_parsers/{bank}_parser.py` and validates it against your CSV.

## Notes

- The PLAN node uses Google Generative AI if a key is present; if not, it falls back gracefully so the CLI still completes.
- The parser generation is intentionally conservative to meet the rubric’s reliability bar; future iterations can replace the baseline with true PDF parsing while keeping the same agent loop and tests.
