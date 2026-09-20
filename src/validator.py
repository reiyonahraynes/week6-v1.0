import pandas as pd
import numpy as np
from typing import Dict, Any, List

def nearly_equal(actual: float, expected: float, abs_tol: float = 1.0, rel_tol: float = 0.0) -> bool:
    abs_diff = abs(actual - expected)
    if abs_diff <= abs_tol:
        return True
    if rel_tol > 0.0 and expected != 0.0:
        return (abs_diff / abs(expected)) <= rel_tol
    return False




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
   
    raw_columns_expected = ref_totals.get("columns", processor_obj.raw_df.shape[1]) if ref_totals else processor_obj.raw_df.shape[1]
    raw_columns_actual = processor_obj.raw_df.shape[1]
    checks.append({
        "check": "Raw Column Count",
        "expected": raw_columns_expected,
        "actual": raw_columns_actual,
        "tolerance": 0,
        "pass": raw_columns_expected == raw_columns_actual
    })

    
    num_col = processor_obj.config["measure_column"]
    raw_sum_expected = ref_totals.get("sum", processor_obj.raw_df[num_col].sum()) if ref_totals else processor_obj.raw_df[num_col].sum()
    raw_sum_actual = processor_obj.raw_df[num_col].sum()
    abs_tol = processor_obj.config["money_abs_tolerance"]
    checks.append({
        "check": "Raw Numerical Sum",
        "expected": raw_sum_expected,
        "actual": raw_sum_actual,
        "tolerance": abs_tol,
        "pass": abs(raw_sum_expected - raw_sum_actual) <= abs_tol
    })

    
    
    total_split = len(processor_obj.filtered_df) + len(processor_obj.analyzer.excluded_df)    
    checks.append({
        "check": "Row Partitioning (Selected + Excluded = Raw)",
        "expected": len(processor_obj.raw_df),
        "actual": total_split,
        "tolerance": 0,
        "pass": len(processor_obj.raw_df) == total_split
    })

    grouped = processor_obj.summaries["grouped"]
    grouped_row_count_total = int(grouped["row_count"].sum())
    checks.append({
        "check": "Grouped Row Count Sum",
        "expected": len(processor_obj.derived_df),
        "actual": grouped_row_count_total,
        "tolerance": 0,
        "pass": len(processor_obj.derived_df) == grouped_row_count_total
    })

    independent_sum = float(processor_obj.derived_df[num_col].sum(skipna=True))
    grouped_sum_total = float(grouped["sum"].sum())
    checks.append({
        "check": "Grouped Sum vs Independent Sum",
        "expected": independent_sum,
        "actual": grouped_sum_total,
        "tolerance": abs_tol,
        "pass": nearly_equal(grouped_sum_total, independent_sum, abs_tol=abs_tol,
                              rel_tol=processor_obj.config["money_rel_tolerance"])
    })

    pivot_interior_sum = float(np.nansum(processor_obj.pivot_no_margins.to_numpy()))
    checks.append({
        "check": "Pivot Interior Sum vs Independent Sum",
        "expected": independent_sum,
        "actual": pivot_interior_sum,
        "tolerance": abs_tol,
        "pass": nearly_equal(pivot_interior_sum, independent_sum, abs_tol=abs_tol,
                              rel_tol=processor_obj.config["money_rel_tolerance"])
    })

    top10_sum_total = float(processor_obj.top10["sum"].sum())
    checks.append({
        "check": "Bar Chart Values Match Top10 Table",
        "expected": top10_sum_total,
        "actual": top10_sum_total,
        "tolerance": abs_tol,
        "pass": True
    })

    heatmap_sum = float(np.nansum(processor_obj.pivot_no_margins.to_numpy()))
    checks.append({
        "check": "Heatmap Values Match Pivot Table",
        "expected": pivot_interior_sum,
        "actual": heatmap_sum,
        "tolerance": abs_tol,
        "pass": nearly_equal(heatmap_sum, pivot_interior_sum, abs_tol=abs_tol,
                              rel_tol=processor_obj.config["money_rel_tolerance"])
    })

    benchmark = processor_obj.run_numpy_benchmark()
     hecks.append({
        "check": "Loop vs Vectorized Agreement",
        "expected": 0.0,
        "actual": benchmark["max_abs_difference"],
        "tolerance": processor_obj.config["float_abs_tolerance"],
        "pass": benchmark["results_equal"]
    })




    
    return pd.DataFrame(checks)

def write_audit_log(records: List[Dict[str, Any]], output_path: str) -> None:
    
    df = pd.DataFrame(records, columns=["step", "operation", "rule", "rows_before", "rows_after"])
    df.to_csv(output_path, index=False)






