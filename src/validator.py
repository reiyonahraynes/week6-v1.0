import pandas as pd
import numpy as np
from typing import Dict, Any, List

def run_reconciliation_checks(processor_obj, ref_totals: Dict[str, Any] = None) -> pd.DataFrame:
    checks = []

    raw_rows_expected = ref_totals.get("rows", len(processor_obj.raw_df)) if ref_totals else len(processor_obj.raw_df)
    raw_rows_actual = len(processor_obj.raw_df)
    checks.append({
        "check": "Raw Row Count",
        "expected": raw_rows_expected,
        "actual": raw_rows_actual,
        "tolerance": 0,
        "pass": raw_rows_expected == raw_rows_actual
    })

    num_col = processor_obj.config["required_columns"][2]
    raw_sum_expected = ref_totals.get("sum", processor_obj.raw_df[num_col].sum()) if ref_totals else processor_obj.raw_df[num_col].sum()
    raw_sum_actual = processor_obj.raw_df[num_col].sum()
    abs_tol = processor_obj.config["tolerance_abs"]
    checks.append({
        "check": "Raw Numerical Sum",
        "expected": raw_sum_expected,
        "actual": raw_sum_actual,
        "tolerance": abs_tol,
        "pass": abs(raw_sum_expected - raw_sum_actual) <= abs_tol
    })

    total_split = len(processor_obj.selected_df) + len(processor_obj.excluded_df)
    checks.append({
        "check": "Row Partitioning (Selected + Excluded = Raw)",
        "expected": len(processor_obj.raw_df),
        "actual": total_split,
        "tolerance": 0,
        "pass": len(processor_obj.raw_df) == total_split
    })

    return pd.DataFrame(checks)
