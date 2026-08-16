import os
import glob
import json
import gc
import sys
import pyarrow.parquet as pq
import pandas as pd
import numpy as np

# Set standard output encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r"C:\Users\Sahithi\Desktop\ainids"

def clean_label(label):
    if not isinstance(label, str):
        return str(label)
    # Replace non-ascii / bad characters
    cleaned = label.replace('\ufffd', '-').replace('\x96', '-')
    # Normalize spaces
    cleaned = ' '.join(cleaned.split())
    # Handle known CICIDS2017 label variations
    if 'Web Attack' in cleaned:
        if 'Brute Force' in cleaned:
            return 'Web Attack - Brute Force'
        elif 'XSS' in cleaned:
            return 'Web Attack - XSS'
        elif 'Sql' in cleaned or 'SQL' in cleaned:
            return 'Web Attack - SQL Injection'
        return cleaned
    return cleaned

def inspect_all():
    files = sorted(glob.glob(os.path.join(DATA_DIR, "*.parquet")))
    print(f"Found {len(files)} parquet files in {DATA_DIR}\n")
    
    total_rows = 0
    total_bytes = 0
    file_summaries = []
    global_label_counts = {}
    schema_map = {}
    
    # We will also track per-column missing and infinite counts across all files
    col_null_counts = {}
    col_inf_counts = {}
    col_dtypes = {}
    col_min_max = {}
    
    for fpath in files:
        fname = os.path.basename(fpath)
        fsize = os.path.getsize(fpath)
        total_bytes += fsize
        
        pfile = pq.ParquetFile(fpath)
        num_rows = pfile.metadata.num_rows
        num_cols = pfile.metadata.num_columns
        schema_names = [col for col in pfile.schema.names]
        schema_map[fname] = schema_names
        total_rows += num_rows
        
        # Identify label col
        label_col = next((c for c in schema_names if 'label' in c.lower()), None)
        
        print(f"=== Inspecting {fname} ===")
        print(f"Path: {fpath}")
        print(f"Size: {fsize:,} bytes ({fsize / (1024*1024):.2f} MB)")
        print(f"Rows: {num_rows:,} | Cols: {num_cols}")
        print(f"Label Col: {label_col}")
        
        # Read file in chunks / row groups or read table efficiently
        # Since memory is 8GB, read in row groups or batches
        file_label_counts = {}
        file_null_counts = {}
        file_inf_counts = {}
        
        for rg in range(pfile.num_row_groups):
            df_rg = pfile.read_row_group(rg).to_pandas()
            
            # Clean label
            if label_col and label_col in df_rg.columns:
                df_rg[label_col] = df_rg[label_col].apply(clean_label)
                rg_vc = df_rg[label_col].value_counts().to_dict()
                for k, v in rg_vc.items():
                    file_label_counts[k] = file_label_counts.get(k, 0) + v
                    global_label_counts[k] = global_label_counts.get(k, 0) + v
            
            # Track nulls & infs
            for c in df_rg.columns:
                if c not in col_dtypes:
                    col_dtypes[c] = str(df_rg[c].dtype)
                
                n_null = int(df_rg[c].isnull().sum())
                if n_null > 0:
                    file_null_counts[c] = file_null_counts.get(c, 0) + n_null
                    col_null_counts[c] = col_null_counts.get(c, 0) + n_null
                
                if pd.api.types.is_numeric_dtype(df_rg[c]):
                    n_inf = int(np.isinf(df_rg[c]).sum())
                    if n_inf > 0:
                        file_inf_counts[c] = file_inf_counts.get(c, 0) + n_inf
                        col_inf_counts[c] = col_inf_counts.get(c, 0) + n_inf
            
            del df_rg
            gc.collect()
            
        print(f"Labels in {fname}:")
        for lbl, cnt in sorted(file_label_counts.items(), key=lambda x: -x[1]):
            print(f"  - {lbl}: {cnt:,} ({cnt/num_rows*100:.2f}%)")
        print(f"Cols with Nulls: {file_null_counts}")
        print(f"Cols with Infs: {file_inf_counts}")
        print()
        
        file_summaries.append({
            "file_name": fname,
            "file_path": fpath,
            "size_bytes": fsize,
            "size_mb": round(fsize / (1024*1024), 2),
            "rows": num_rows,
            "columns_count": num_cols,
            "label_column": label_col,
            "label_counts": {str(k): int(v) for k, v in file_label_counts.items()},
            "null_counts": file_null_counts,
            "inf_counts": file_inf_counts
        })

    # Schema consistency analysis
    all_col_lists = list(schema_map.values())
    first_col_list = all_col_lists[0]
    identical_schemas = all(cols == first_col_list for cols in all_col_lists)
    
    print("\n" + "="*70)
    print("DATASET GLOBAL SUMMARY")
    print("="*70)
    print(f"Total Parquet Files: {len(files)}")
    print(f"Total Dataset Size: {total_bytes:,} bytes ({total_bytes / (1024*1024):.2f} MB)")
    print(f"Total Rows: {total_rows:,}")
    print(f"Total Columns per file: {len(first_col_list)}")
    print(f"All files have identical columns/schema? {identical_schemas}")
    
    print("\nGlobal Class Distribution:")
    for lbl, cnt in sorted(global_label_counts.items(), key=lambda x: -x[1]):
        print(f"  {lbl:35s}: {cnt:10,d} ({cnt/total_rows*100:6.3f}%)")
        
    print("\nColumns with Null Values across entire dataset:")
    for c, cnt in col_null_counts.items():
        print(f"  {c}: {cnt:,} nulls ({cnt/total_rows*100:.4f}%)")
    if not col_null_counts:
        print("  None! No null values detected.")
        
    print("\nColumns with Infinite Values across entire dataset:")
    for c, cnt in col_inf_counts.items():
        print(f"  {c}: {cnt:,} infs ({cnt/total_rows*100:.4f}%)")
    if not col_inf_counts:
        print("  None! No infinite values detected.")

    print("\nColumns and Data Types:")
    for idx, c in enumerate(first_col_list):
        print(f"  {idx+1:2d}. {c:40s} : {col_dtypes.get(c, 'unknown')}")

    # Save detailed JSON report
    report_data = {
        "dataset_name": "CICIDS2017 (Pre-extracted Parquet)",
        "total_files": len(files),
        "total_bytes": total_bytes,
        "total_size_mb": round(total_bytes / (1024*1024), 2),
        "total_rows": total_rows,
        "total_columns": len(first_col_list),
        "identical_schemas": identical_schemas,
        "columns": first_col_list,
        "column_dtypes": col_dtypes,
        "global_label_counts": {str(k): int(v) for k, v in global_label_counts.items()},
        "columns_with_nulls": col_null_counts,
        "columns_with_infs": col_inf_counts,
        "files": file_summaries
    }
    
    os.makedirs("reports", exist_ok=True)
    with open(os.path.join("reports", "dataset_inspection.json"), "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    print("\nDetailed inspection saved to reports/dataset_inspection.json")

if __name__ == "__main__":
    inspect_all()
