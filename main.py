import os
import pandas as pd
from config import CONFIG
from src.processor import DataProcessor
from src.validator import run_reconciliation_checks

def main() -> None
    processor = DataProcessor(CONFIG)
    
    try:
        processor.load_data()
        processor.process_and_filter()
    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"Execution Halted: {e}")
        exit(1)

    customs_reference = {
        "rows": 2236612,
        "sum": 3587267375257.0
    }

    processor.generate_outputs()

    bench_results = processor.run_numpy_benchmark()

    
    val_df = run_reconciliation_checks(processor, customs_reference)
    os.makedirs(CONFIG["output_dir"], exist_ok=True)
    val_df.to_csv(os.path.join(CONFIG["output_dir"], "validation.csv"), index=False)

    if not val_df["pass"].all():
        print("Validation failure detected! Review validation.csv for details.")
        exit(1)
    else:
        print("All validation and reconciliation checks passed successfully.")

    processor.generate_outputs()

    audit_log = pd.DataFrame(processor.audit_records)
    audit_log.to_csv(os.path.join(CONFIG["output_dir"], "audit_log.csv"), index=False)

    bench_results = processor.run_numpy_benchmark()
    print(f"NumPy Benchmark - Vectorized time: {bench_results['median_vector_time']:.6f}s | Loop time: {bench_results['median_loop_time']:.6f}s")
    print("Pipeline completed successfully. All deliverables created in outputs/.")

if __name__ == "__main__":
    main()
