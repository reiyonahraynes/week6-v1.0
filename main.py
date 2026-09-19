import os
import sys
import pandas as pd
from config import CONFIG, REQUIRED_COLUMNS
from src.processor import DataProcessor
from src.validator import run_reconciliation_checks

def main() -> None
    processor = DataProcessor(CONFIG)
    
    try:
        processor.load_data()
    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"Execution Halted: {e}")
        sys.exit(1)
    
    raw_rows, raw_columns = processor.raw_df.shape
    print(f"Loaded {raw_rows:,} rows and {raw_columns} columns from {CONFIG['input_path']}")

    print("\n--- Inspection ---")
    print(f"Row count: {raw_rows:,}   Column count: {raw_columns}")
    print("Column dtypes:")
    print(processor.raw_df.dtypes.to_string())
    missing_counts = processor.raw_df[list(REQUIRED_COLUMNS)].isna().sum()
    print("\nMissing-value counts in required columns:")
    print(missing_counts.to_string())

    try:
        processor.process_and_filter()
    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"Execution Halted: {e}")
        sys.exit(1)

     print(
        f"\nFiltered to {len(processor.filtered_df):,} rows "
        f"(excluded {len(processor.analyzer.excluded_df):,}: "
        f"{processor.analyzer.filter_breakdown})"
        )

    measure_col = CONFIG["measure_column"]
    sorted_preview = processor.derived_df.sort_values(by=measure_col, ascending=False).head(10)
    print("\nTop 10 individual records by dutiable value (sorting demonstration):")
    print(
        sorted_preview[
            [CONFIG["category_columns"][0], CONFIG["category_columns"][1], measure_col]
        ].to_string(index=False)
    )


    
    
    customs_reference = {
        "rows": 2236612,
        "columns": 30,
        "sum": 3587267375257.0
    }

    processor.generate_outputs()

    print(
        f"\nWrote grouped.csv ({len(processor.summaries['grouped'])} groups), "
        f"grouped_two.csv ({len(processor.summaries['grouped_two'])} groups), "
        f"pivot.csv, and top10.csv"
    )
    print(
        f"\nWrote {os.path.join(CONFIG['output_dir'], 'bar.png')} and "
        f"{os.path.join(CONFIG['output_dir'], 'heatmap.png')}"
    )


    bench_results = processor.run_numpy_benchmark()

    print("\n--- NumPy loop vs. vectorized comparison ---")
    print(
        f"Sample size: {bench_results['sample_size']:,}   "
        f"Results equal: {bench_results['results_equal']}   "
        f"Max abs difference: {bench_results['max_abs_difference']:.2e}"
    )
    print(
        f"Median loop time: {bench_results['median_loop_time']:.6f}s   "
        f"Median vectorized time: {bench_results['median_vector_time']:.6f}s"
    )


    val_df = run_reconciliation_checks(processor, customs_reference)
    os.makedirs(CONFIG["output_dir"], exist_ok=True)
    val_df.to_csv(os.path.join(CONFIG["output_dir"], "validation.csv"), index=False)

    audit_log = pd.DataFrame(processor.audit_records)
    audit_log.to_csv(os.path.join(CONFIG["output_dir"], "audit_log.csv"), index=False)




    print("\n--- Validation summary ---")
    print(val_df.to_string(index=False))

    if not val_df["pass"].all():
        failed = val_df[~val_df["pass"]]
        print("\nVALIDATION FAILED. The following checks did not pass:")
        print(failed.to_string(index=False))
        sys.exit(2)

    print("\nAll validation and reconciliation checks passed successfully.")
    print("Pipeline completed successfully. All deliverables created in outputs/.")

if __name__ == "__main__":
    main()
