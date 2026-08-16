import os
import glob
import json
import gc
import pyarrow.parquet as pq
import pandas as pd
import numpy as np

DATA_DIR = r"C:\Users\Sahithi\Desktop\ainids"

def inspect_all():
    files = sorted(glob.glob(os.path.join(DATA_DIR, "*.parquet")))
    print(f"Found {len(files)} parquet files in {DATA_DIR}:\n")
    
    total_rows = 0
    total_bytes = 0
    all_schemas = {}
    label_counts_per_file = {}
    global_label_counts = {}
    column_sets = {}
    file_summaries = []

    for fpath in files:
        fname = os.path.basename(fpath)
        fsize = os.path.getsize(fpath)
        total_bytes += fsize
        
        # Read parquet metadata without loading full data
        pfile = pq.ParquetFile(fpath)
        num_rows = pfile.metadata.num_rows
        num_cols = pfile.metadata.num_columns
        schema_names = pfile.schema.names
        total_rows += num_rows
        column_sets[fname] = set(schema_names)
        
        print(f"File: {fname}")
        print(f"  Path: {fpath}")
        print(f"  Size: {fsize:,} bytes ({fsize / (1024*1024):.2f} MB)")
        print(f"  Rows: {num_rows:,}")
        print(f"  Columns: {num_cols}")
        
        # Check label column
        label_col = None
        for col in schema_names:
            if 'label' in col.lower():
                label_col = col
                break
        print(f"  Label column identified: {label_col}")
        
        # Read target column and check value counts
        if label_col:
            df_label = pfile.read([label_col]).to_pandas()
            vc = df_label[label_col].value_counts(dropna=False).to_dict()
            label_counts_per_file[fname] = vc
            for k, v in vc.items():
                global_label_counts[k] = global_label_counts.get(k, 0) + v
            print(f"  Unique Labels: {list(vc.keys())}")
            print(f"  Value counts: {vc}")
            del df_label
            gc.collect()
        
        # Read a batch / sample to check dtypes, nulls, infs
        # Read first row group or table to check types
        sample_df = pfile.read_row_group(0).to_pandas()
        
        # Check nulls and infs in this sample
        null_counts = sample_df.isnull().sum().to_dict()
        cols_with_nulls = {k: v for k, v in null_counts.items() if v > 0}
        
        # Check infinite values in numeric columns
        numeric_cols = sample_df.select_dtypes(include=[np.number]).columns.tolist()
        non_numeric_cols = sample_df.select_dtypes(exclude=[np.number]).columns.tolist()
        
        inf_cols = {}
        for c in numeric_cols:
            n_inf = np.isinf(sample_df[c]).sum()
            if n_inf > 0:
                inf_cols[c] = int(n_inf)
                
        constant_cols = [c for c in sample_df.columns if sample_df[c].nunique() <= 1]
        
        file_summaries.append({
            "name": fname,
            "path": fpath,
            "size_bytes": fsize,
            "rows": num_rows,
            "cols": num_cols,
            "label_col": label_col,
            "labels": list(vc.keys()) if label_col else [],
            "label_counts": {str(k): int(v) for k, v in vc.items()} if label_col else {},
            "cols_with_nulls_in_sample": cols_with_nulls,
            "inf_cols_in_sample": inf_cols,
            "constant_cols_in_sample": constant_cols,
            "numeric_cols_count": len(numeric_cols),
            "non_numeric_cols": non_numeric_cols,
            "sample_rows": len(sample_df)
        })
        
        del sample_df
        gc.collect()
        print("-" * 60)

    # Check schema consistency across files
    first_cols = list(column_sets.values())[0]
    all_same = all(cols == first_cols for cols in column_sets.values())
    print(f"\nAll files have identical columns? {all_same}")
    if not all_same:
        base_cols = set(list(column_sets.values())[0])
        for fname, cols in column_sets.items():
            diff1 = cols - base_cols
            diff2 = base_cols - cols
            if diff1 or diff2:
                print(f"Diff for {fname}: Extra={diff1}, Missing={diff2}")

    print("\n" + "=" * 60)
    print(f"GLOBAL SUMMARY:")
    print(f"Total Files: {len(files)}")
    print(f"Total Size: {total_bytes:,} bytes ({total_bytes / (1024*1024):.2f} MB)")
    print(f"Total Records across dataset: {total_rows:,}")
    print(f"Global Label Counts:")
    for k, v in sorted(global_label_counts.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v:,} ({v / total_rows * 100:.3f}%)")
    print("=" * 60)

    # Save detailed inspection result to JSON
    with open("dataset_inspection_raw.json", "w") as out:
        json.dump({
            "total_files": len(files),
            "total_bytes": total_bytes,
            "total_rows": total_rows,
            "global_label_counts": {str(k): int(v) for k, v in global_label_counts.items()},
            "column_names": sorted(list(first_cols)),
            "all_files_identical_columns": all_same,
            "file_summaries": file_summaries
        }, out, indent=2)

if __name__ == "__main__":
    inspect_all()
