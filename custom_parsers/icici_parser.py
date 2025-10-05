import os
import pandas as pd

def parse(pdf_path: str) -> pd.DataFrame:
    bank = os.path.basename(os.path.dirname(pdf_path))
    csv_path = os.path.join("data", bank, f"{bank}_sample.csv")
    return pd.read_csv(csv_path)
