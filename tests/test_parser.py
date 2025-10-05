import pandas as pd
from pandas.testing import assert_frame_equal
from custom_parsers.icici_parser import parse

def test_icici_parser():
    """
    Tests the ICICI parser against a sample PDF and its ground-truth CSV.
    """
    pdf_path = "data/icici/icici_sample.pdf"
    csv_path = "data/icici/icici_sample.csv"

    result_df = parse(pdf_path)
    expected_df = pd.read_csv(csv_path)

    assert_frame_equal(result_df, expected_df, check_dtype=False)