import pandas as pd
from pandas.testing import assert_frame_equal
import importlib.util
import sys
import os
import traceback

def run_parser_and_test(code: str, bank: str, pdf_path: str, csv_path: str) -> str:
    """
    Saves generated Python code, runs it, and compares the output to a sample CSV.
    Returns "Success" or a detailed error traceback string.
    """
    parser_dir = "custom_parsers"
    # The agent will write the file here, so we don't need to create it.
    parser_path = os.path.join(parser_dir, f"{bank}_parser.py")

    with open(parser_path, "w") as f:
        f.write(code)
    
    try:
        spec = importlib.util.spec_from_file_location(f"{bank}_parser", parser_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        print(f"--- Running generated parser: {parser_path} ---")
        result_df = module.parse(pdf_path)
        expected_df = pd.read_csv(csv_path)

        assert_frame_equal(result_df, expected_df, check_dtype=False)
        
        print("--- Parser Test SUCCEEDED ---")
        return "Success"
        
    except Exception:
        error_str = traceback.format_exc()
        print(f"--- Parser Test FAILED ---\n{error_str}")
        return error_str