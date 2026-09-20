# Philippine Customs 2015 Import Records 
A python program that loads, filters, transfroms, and summarize the data of the Philippine Bureau of Customs 2015 dataset. It generates summary tables, and plots.

# The data source came from 2015.csv 
Source: Philippine Customs dataset, BetterGov.PH
File size: 493.5 MB

# Background
The data was extracted from Bureau of Customs e2m system. The 2012–2019 slice of the dataset (which includes 2015) was originally compiled and released by Ken Abante in 2020.

## Setup
bash
python -m venv .venv
source .venv/bin/activate  
pip install -r requirements.txt

# Please install the 2015.csv
Place the raw 2015.csv file at 'data/2015.csv' (see above), then run:

bash
python main.py

The program prints an inspection summary, a sorting demonstration, the
NumPy comparison, a validation summary, and writes all required output files to outputs/. It exits with status 0 if all validation checks pass.


It loads data, filters to Consumption entries (entry==c) with a positive dutiable value, and excludes the other rows.

It writes group.csv, group_two.csv, pivot.csv, top10.csv, bar.png, heatmap.png, validation.csv, and audit_log.csv to outputs

It runs 10 reconcilliation checks including raw row or column counts, raw total dutiable value, kept and excluded row reconciliation, group/pivot totals, and plot-data consistency. If any check fails it prints the failing rows and exits nonzero.

It compares a pure-python loop against NumPy vectorized tax-rate calculation on the fixed-seed sample of 20,000 reocrds. The vectorized version is faster and the code is split across main.py, config.py, src/processor.py, and src/validator.py with a notebook and HTML export.





