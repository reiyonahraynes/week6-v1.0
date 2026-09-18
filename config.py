
REQUIRED_COLUMNS: set[str] = {
    "uid",
    "tq",
    "entry",
    "countryorigin_iso3",
    "dutiablevaluephp",
    "dutiestaxes",
}


DTYPE_MAP: dict[str, any] = {
    "uid": str,
    "ty": str,
    "tq": str,
    "tm": str,
    "entry": str,
    "hscode": str,
    "goodsdescription": str,
    "p": "float64",
    "q": "float64",
    "m_fob": "float64",
    "m_cif": "float64",
    "fx_usd": "float64",
    "dutiablevalueforeign": "float64",
    "exchangerate": "float64",
    "currency": str,
    "dutiablevaluephp": "float64",
    "dutypaid": "float64",
    "exciseadvalorem": "float64",
    "arrastre": "float64",
    "wharfage": "float64",
    "vatbase": "float64",
    "vatpaid": "float64",
    "othertax": "float64",
    "finesandpenalties": "float64",
    "dutiestaxes": "float64",
    "prefcode": str,
    "countryorigin_iso3": str,
    "countryexport_iso3": str,
    "subport": str,
    "port": str,
}


CONFIG: dict[str, any] = {
    # --- input ---
    "input_path": "data/2015.csv",
    "encoding": "latin1",         
    "chunksize": 300_000,          
    "dtype_map": DTYPE_MAP,

   
    "category_columns": ["countryorigin_iso3", "tq"],   
    "measure_column": "dutiablevaluephp",               

   
    "filter_entry_type": "C",
    "min_measure_value": 0.0,      

   
    "effective_tax_rate_column": "effective_tax_rate_pct",
   
    "high_value_threshold_php": 1_000_000.0,
    "value_tier_column": "value_tier",

    "output_dir": "outputs",
    "top_n": 10,

    "random_seed": 42,
    "sample_size": 20_000,
    "timing_repeats": 5,

    "count_tolerance": 0,         
    "money_abs_tolerance": 1.00,   
    "money_rel_tolerance": 0.0,   
    "float_abs_tolerance": 1e-6,  

    "reference_totals": {
        "rows": 2_236_612,
        "columns": 30,
        "dutiablevaluephp_sum": 3_587_267_375_257.0,
        "sha256": "b3b5a3a95340179a716a05611d51ad4906484d38363d1ac36494a404c04e4370",
    },
}
