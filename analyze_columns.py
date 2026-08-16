import os
import glob
import json
import pyarrow.parquet as pq
import pandas as pd
import numpy as np

DATA_DIR = r"C:\Users\Sahithi\Desktop\ainids"

def analyze_columns():
    files = sorted(glob.glob(os.path.join(DATA_DIR, "*.parquet")))
    
    # We will sample 100,000 rows across files or calculate min/max incrementally
    # Let's compute global min, max, std incrementally for each feature
    first_file = pq.ParquetFile(files[0])
    feature_cols = [c for c in first_file.schema.names if 'label' not in c.lower()]
    
    mins = {c: float('inf') for c in feature_cols}
    maxs = {c: float('-inf') for c in feature_cols}
    sums = {c: 0.0 for c in feature_cols}
    total_count = 0
    
    # Also check constant columns
    for fpath in files:
        pfile = pq.ParquetFile(fpath)
        for rg in range(pfile.num_row_groups):
            df = pfile.read_row_group(rg, columns=feature_cols).to_pandas()
            for c in feature_cols:
                c_min = float(df[c].min())
                c_max = float(df[c].max())
                if c_min < mins[c]:
                    mins[c] = c_min
                if c_max > maxs[c]:
                    maxs[c] = c_max
                sums[c] += float(df[c].sum())
            total_count += len(df)
            del df

    constant_cols = [c for c in feature_cols if mins[c] == maxs[c]]
    print(f"Total Rows Checked: {total_count:,}")
    print(f"Constant Columns (min == max across all 2.31M rows): {len(constant_cols)}")
    for c in constant_cols:
        print(f"  - {c} (constant value: {mins[c]})")
        
    results = {
        "total_rows": total_count,
        "constant_columns": constant_cols,
        "feature_ranges": {c: {"min": mins[c], "max": maxs[c], "mean": sums[c]/total_count} for c in feature_cols}
    }
    
    with open("reports/column_analysis.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved to reports/column_analysis.json")

if __name__ == "__main__":
    analyze_columns()
