
import os
import statistics
import time
from typing import Any, Dict, Optional, Set

import matplotlib

matplotlib.use("Agg")  # no display needed
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


# Loading area


def load_data(
    path: str,
    required_columns: Set[str],
    encoding: str = "latin1",
    chunksize: int = 300_000,
    dtype_map: Dict[str, Any] | None = None,
) -> pd.DataFrame:

#Validates the columns in requred columns and presents it

#ARGS is path to the csv file on disk

  
    #invalid input is missing file
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Input file not found: '{path}'. Download the dataset named in "
            f"the README and place it at this path before running main.py."
        )

    reader = pd.read_csv(
        path,
        encoding=encoding,
        chunksize=chunksize,
        dtype=dtype_map,
        low_memory=False,
    )

    chunks = []
    header_checked = False

    # loop over the file in chunks 
    for chunk in reader:
        if not header_checked:
            # invalid input goes missing required column 
            missing = required_columns - set(chunk.columns)
            if missing:
                raise ValueError(
                    "Input file is missing required column(s): "
                    f"{sorted(missing)}. Found columns: {sorted(chunk.columns)}"
                )
            header_checked = True
        chunks.append(chunk)

    return pd.concat(chunks, ignore_index=True)



# Filter, derive and summarize

class CustomsAnalyzer:


    def __init__(self, df: pd.DataFrame, config: Dict[str, Any]) -> None:
       
        self.df = df
        self.config = config
        self.excluded_df: pd.DataFrame = pd.DataFrame()
        self.filter_breakdown: Dict[str, int] = {}

    def filter_records(self) -> pd.DataFrame:
      
        #Returns:
            #The filtered DataFrame (new onject so original is untouched).
       
        entry_col = "entry"
        measure_col = self.config["measure_column"]
        entry_type = self.config["filter_entry_type"]
        min_value = self.config["min_measure_value"]

        condition_entry = self.df[entry_col] == entry_type
        condition_measure = self.df[measure_col].notna() & (
            self.df[measure_col] > min_value
        )

        keep_mask = condition_entry & condition_measure
        filtered = self.df.loc[keep_mask, :].copy()
        self.excluded_df = self.df.loc[~keep_mask, :].copy()

        # Explain the exclusions for the README / audit log.
        missing_entry = int(self.df[entry_col].isna().sum())
        wrong_entry_type = int(
            (self.df[entry_col].notna() & (self.df[entry_col] != entry_type)).sum()
        )
        invalid_measure = int((~condition_measure & condition_entry).sum())
        self.filter_breakdown = {
            "missing_entry_value": missing_entry,
            "other_entry_type": wrong_entry_type,
            "invalid_measure_value": invalid_measure,
        }

        return filtered

    def add_derived_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        #Add one numerical and one category orflag derived column


        #value tier - configure threshhold

        #args - df: data frames with filter records.

        #returns A copy of ``df`` with the two derived columns.
   
        measure_col = self.config["measure_column"]
        rate_col = self.config["effective_tax_rate_column"]
        tier_col = self.config["value_tier_column"]
        threshold = self.config["high_value_threshold_php"]

        result = df.copy()

        dutiable_value = result[measure_col].to_numpy(dtype="float64")
        duties_taxes = result["dutiestaxes"].fillna(0.0).to_numpy(dtype="float64")
        result[rate_col] = (duties_taxes / dutiable_value) * 100.0

        result[tier_col] = np.where(
            result[measure_col].to_numpy(dtype="float64") >= threshold,
            "High",
            "Low",
        )

        return result

    def summarize(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:

        
        cat_first, cat_second = self.config["category_columns"]
        measure_col = self.config["measure_column"]

        work = df.copy()
        work[cat_first] = work[cat_first].fillna("MISSING")
        work[cat_second] = work[cat_second].fillna("MISSING")
        grouped = (
            work.groupby(cat_first, dropna=False)
            .agg(
                row_count=(measure_col, "size"),
                valid_measure_count=(measure_col, "count"),
                sum=(measure_col, "sum"),
                mean=(measure_col, "mean"),
            )
            .reset_index()
        )
        grouped["missing_measure"] = grouped["row_count"] - grouped["valid_measure_count"]

        # --- grouped_two.csv: group by both categories, named aggs ------
        grouped_two = (
            work.groupby([cat_first, cat_second], dropna=False)
            .agg(
                row_count=(measure_col, "size"),
                sum=(measure_col, "sum"),
            )
            .reset_index()
        )
        pivot = pd.pivot_table(
            work,
            values=measure_col,
            index=cat_first,
            columns=cat_second,
            aggfunc="sum",
            margins=True,
            margins_name="All",
        )

        return {"grouped": grouped, "grouped_two": grouped_two, "pivot": pivot}
        

    
    def get_pivot(self, df: pd.DataFrame) -> pd.DataFrame:
        cat_first = self.config["category_first"]
        cat_second = self.config["category_second"]
        measure = self.config["measure_column"]

        work = df.copy()
        work[cat_first] = work[cat_first].fillna("MISSING")
        work[cat_second] = work[cat_second].fillna("MISSING")

        pivot_table = pd.pivot_table(
            work,
            values=measure,
            index=cat_first,
            columns=cat_second,
            aggfunc="sum",
            margins=True,
            margins_name="Total",
            dropna=False
        )

        return pivot_table

    def get_top10(self, grouped_df: pd.DataFrame) -> pd.DataFrame:
        top10 = grouped_df.sort_values(by="sum", ascending=False).head(10)
        return top10

#bar chart of top 10
    def get_pivot(self, df: pd.DataFrame) -> pd.DataFrame:
        cat_first = self.config["category_first"]
        cat_second = self.config["category_second"]
        measure = self.config["measure_column"]

        work = df.copy()
        work[cat_first] = work[cat_first].fillna("MISSING")
        work[cat_second] = work[cat_second].fillna("MISSING")

        pivot_table = pd.pivot_table(
            work,
            values=measure,
            index=cat_first,
            columns=cat_second,
            aggfunc="sum",
            margins=True,
            margins_name="Total",
            dropna=False
        )

        return pivot_table

    def get_top10(self, grouped_df: pd.DataFrame) -> pd.DataFrame:
        top10 = grouped_df.sort_values(by="sum", ascending=False).head(10)
        return top10


def compare_loop_vs_vectorized(
    dutiable_value: np.ndarray,
    duties_taxes: np.ndarray,
    high_value_threshold: float,
    seed: int = 42,
    sample_size: int = 20_000,
    repeats: int = 5,
) -> Dict[str, Any]:
    
    rng = np.random.default_rng(seed)
    n = dutiable_value.shape[0]
    actual_sample_size = min(sample_size, n)
    sample_idx = rng.choice(n, size=actual_sample_size, replace=False)

    sample_value = dutiable_value[sample_idx]
    sample_taxes = duties_taxes[sample_idx]

    loop_times = []
    loop_result = None
    for _ in range(repeats):
        start = time.perf_counter()
        result = np.empty(actual_sample_size, dtype="float64")
        for i in range(actual_sample_size):
            result[i] = (sample_taxes[i] / sample_value[i]) * 100.0
        loop_times.append(time.perf_counter() - start)
        loop_result = result

    vectorized_times = []
    vectorized_result = None
    for _ in range(repeats):
        start = time.perf_counter()
        vectorized_result = (sample_taxes / sample_value) * 100.0
        vectorized_times.append(time.perf_counter() - start)

    max_abs_difference = float(np.max(np.abs(loop_result - vectorized_result)))
    results_equal = bool(np.allclose(loop_result, vectorized_result, atol=1e-6))

  
    mask = dutiable_value >= high_value_threshold
    boolean_mask_count = int(mask.sum())
    aggregation_sum_high_value = float(dutiable_value[mask].sum())

    return {
        "sample_size": actual_sample_size,
        "results_equal": results_equal,
        "max_abs_difference": max_abs_difference,
        "median_loop_seconds": statistics.median(loop_times),
        "median_vectorized_seconds": statistics.median(vectorized_times),
        "median_loop_time": statistics.median(loop_times),        
        "median_vector_time": statistics.median(vectorized_times),  
        "boolean_mask_count": boolean_mask_count,
        "aggregation_sum_high_value": aggregation_sum_high_value,
    }


def plot_bar_chart(
    top10: pd.DataFrame,
    category_column: str,
    value_column: str,
    output_path: str,
    title: str = "Top 10 Countries of Origin by Dutiable Value",
    value_label: str = "Total Dutiable Value (PHP)",
) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(top10[category_column].astype(str), top10[value_column], color="#2c7fb8")
    ax.set_title(title)
    ax.set_xlabel(category_column)
    ax.set_ylabel(value_label)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_heatmap(
    pivot_no_margins: pd.DataFrame,
    output_path: str,
    title: str = "Dutiable Value by Country of Origin and Quarter",
    value_label: str = "Dutiable Value (PHP)",
    top_rows: Optional[int] = 20,
) -> None:
    data = pivot_no_margins.copy()
    if top_rows is not None and len(data) > top_rows:
        data = data.loc[data.sum(axis=1).sort_values(ascending=False).head(top_rows).index]

    fig, ax = plt.subplots(figsize=(10, max(6, len(data) * 0.35)))
    sns.heatmap(data, cmap="viridis", ax=ax, cbar_kws={"label": value_label})
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


class DataProcessor:
    

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.raw_df: pd.DataFrame = pd.DataFrame()
        self.analyzer: Optional[CustomsAnalyzer] = None
        self.filtered_df: pd.DataFrame = pd.DataFrame()
        self.derived_df: pd.DataFrame = pd.DataFrame()
        self.summaries: Dict[str, pd.DataFrame] = {}
        self.top10: pd.DataFrame = pd.DataFrame()
        self.pivot_no_margins: pd.DataFrame = pd.DataFrame()
        self.audit_records: list = []
        self.benchmark: Optional[Dict[str, Any]] = None

    def load_data(self) -> pd.DataFrame:
        from config import REQUIRED_COLUMNS

        self.raw_df = load_data(
            path=self.config["input_path"],
            required_columns=REQUIRED_COLUMNS,
            encoding=self.config["encoding"],
            chunksize=self.config["chunksize"],
            dtype_map=self.config["dtype_map"],
        )
        self.audit_records.append(
            {
                "step": 1,
                "operation": "load_data",
                "rule": (
                    f"read '{self.config['input_path']}' in chunks of "
                    f"{self.config['chunksize']} rows"
                ),
                "rows_before": 0,
                "rows_after": len(self.raw_df),
            }
        )
        return self.raw_df

    def process_and_filter(self) -> pd.DataFrame:
        measure_col = self.config["measure_column"]
        raw_rows = len(self.raw_df)

        self.analyzer = CustomsAnalyzer(self.raw_df, self.config)
        self.filtered_df = self.analyzer.filter_records()

        if len(self.filtered_df) == 0:
            raise ValueError(
                f"The configured filter (entry == "
                f"'{self.config['filter_entry_type']}' and {measure_col} > "
                f"{self.config['min_measure_value']}) returned zero rows. "
                "Check the filter settings in config.py."
            )

        self.audit_records.append(
            {
                "step": 2,
                "operation": "filter_records",
                "rule": (
                    f"keep entry == '{self.config['filter_entry_type']}' AND "
                    f"{measure_col} > {self.config['min_measure_value']}; rows "
                    "with missing entry value are placed in the excluded group"
                ),
                "rows_before": raw_rows,
                "rows_after": len(self.filtered_df),
            }
        )
        for reason, count in self.analyzer.filter_breakdown.items():
            self.audit_records.append(
                {
                    "step": 2,
                    "operation": "exclusion_breakdown",
                    "rule": reason,
                    "rows_before": raw_rows,
                    "rows_after": count,
                }
            )

        self.derived_df = self.analyzer.add_derived_columns(self.filtered_df)
        self.audit_records.append(
            {
                "step": 3,
                "operation": "add_derived_columns",
                "rule": (
                    f"add '{self.config['effective_tax_rate_column']}' "
                    f"(numerical) and '{self.config['value_tier_column']}' "
                    f"(category/flag, threshold PHP "
                    f"{self.config['high_value_threshold_php']:,.0f})"
                ),
                "rows_before": len(self.filtered_df),
                "rows_after": len(self.derived_df),
            }
        )

        self.summaries = self.analyzer.summarize(self.derived_df)
        grouped = self.summaries["grouped"]
        pivot = self.summaries["pivot"]

        self.top10 = (
            grouped.sort_values("sum", ascending=False)
            .head(self.config["top_n"])
            .reset_index(drop=True)
        )
        self.pivot_no_margins = pivot.drop(index="All", errors="ignore").drop(
            columns="All", errors="ignore"
        )

        self.audit_records.append(
            {
                "step": 4,
                "operation": "summarize",
                "rule": (
                    f"group by {self.config['category_columns'][0]}; group by "
                    f"both categories with named aggregations; pivot_table "
                    f"with margins; top {self.config['top_n']} by sum"
                ),
                "rows_before": len(self.derived_df),
                "rows_after": len(grouped),
            }
        )
        return self.derived_df

    def run_numpy_benchmark(self) -> Dict[str, Any]:
        if self.benchmark is not None:
            return self.benchmark

        measure_col = self.config["measure_column"]
        dutiable_array = self.derived_df[measure_col].to_numpy(dtype="float64")
        taxes_array = self.derived_df["dutiestaxes"].fillna(0.0).to_numpy(dtype="float64")

        result = compare_loop_vs_vectorized(
            dutiable_value=dutiable_array,
            duties_taxes=taxes_array,
            high_value_threshold=self.config["high_value_threshold_php"],
            seed=self.config["random_seed"],
            sample_size=self.config["sample_size"],
            repeats=self.config["timing_repeats"],
        )

        self.audit_records.append(
            {
                "step": 5,
                "operation": "numpy_loop_vs_vectorized",
                "rule": (
                    f"seed={self.config['random_seed']}, sample_size="
                    f"{result['sample_size']}, repeats="
                    f"{self.config['timing_repeats']}"
                ),
                "rows_before": len(self.derived_df),
                "rows_after": result["sample_size"],
            }
        )

        self.benchmark = result
        return result

    def generate_outputs(self) -> Dict[str, str]:
        output_dir = self.config["output_dir"]
        os.makedirs(output_dir, exist_ok=True)

        paths = {
            "grouped": os.path.join(output_dir, "grouped.csv"),
            "grouped_two": os.path.join(output_dir, "grouped_two.csv"),
            "pivot": os.path.join(output_dir, "pivot.csv"),
            "top10": os.path.join(output_dir, "top10.csv"),
            "bar": os.path.join(output_dir, "bar.png"),
            "heatmap": os.path.join(output_dir, "heatmap.png"),
        }

        self.summaries["grouped"].to_csv(paths["grouped"], index=False)
        self.summaries["grouped_two"].to_csv(paths["grouped_two"], index=False)
        self.summaries["pivot"].to_csv(paths["pivot"])
        self.top10.to_csv(paths["top10"], index=False)

        plot_bar_chart(
            top10=self.top10,
            category_column=self.config["category_columns"][0],
            value_column="sum",
            output_path=paths["bar"],
        )
        plot_heatmap(
            pivot_no_margins=self.pivot_no_margins,
            output_path=paths["heatmap"],
        )

        self.audit_records.append(
            {
                "step": 6,
                "operation": "generate_outputs",
                "rule": (
                    "write grouped.csv, grouped_two.csv, pivot.csv, "
                    "top10.csv, bar.png, heatmap.png"
                ),
                "rows_before": len(self.derived_df),
                "rows_after": len(self.summaries["grouped"]),
            }
        )
        return paths
