import os
import glob
import gc
import json
import pyarrow.parquet as pq
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

DATA_DIR = r"C:\Users\Sahithi\Desktop\ainids"
PROCESSED_DIR = os.path.join(DATA_DIR, "data", "processed")

# Canonical class labels
CANONICAL_CLASSES = [
    "Benign",
    "DoS Hulk",
    "DDoS",
    "DoS GoldenEye",
    "FTP-Patator",
    "DoS slowloris",
    "DoS Slowhttptest",
    "SSH-Patator",
    "PortScan",
    "Web Attack - Brute Force",
    "Bot",
    "Web Attack - XSS",
    "Infiltration",
    "Web Attack - SQL Injection",
    "Heartbleed"
]

# Max samples to retain per high-volume class (to fit 8GB RAM safely)
MAX_SAMPLES_PER_MAJOR_CLASS = 20000

def clean_label(label):
    if not isinstance(label, str):
        return str(label)
    cleaned = label.replace('\ufffd', '-').replace('\x96', '-')
    cleaned = ' '.join(cleaned.split())
    if 'Web Attack' in cleaned:
        if 'Brute Force' in cleaned:
            return 'Web Attack - Brute Force'
        elif 'XSS' in cleaned:
            return 'Web Attack - XSS'
        elif 'Sql' in cleaned or 'SQL' in cleaned:
            return 'Web Attack - SQL Injection'
        return cleaned
    return cleaned

def load_and_sample_dataset(data_dir=DATA_DIR, random_state=42):
    """
    Memory-efficient row-group loader for CICIDS2017 parquet files.
    Preserves 100% of minority attack classes and samples high-volume classes.
    """
    np.random.seed(random_state)
    files = sorted(glob.glob(os.path.join(data_dir, "*.parquet")))
    if not files:
        raise FileNotFoundError(f"No parquet files found in {data_dir}")
    
    print(f"[DataLoader] Found {len(files)} parquet files. Processing row groups...")
    
    # Store collected dataframes per class
    class_pools = {cls_name: [] for cls_name in CANONICAL_CLASSES}
    
    for fpath in files:
        fname = os.path.basename(fpath)
        pfile = pq.ParquetFile(fpath)
        schema_names = pfile.schema.names
        label_col = next((c for c in schema_names if 'label' in c.lower()), None)
        
        print(f"[DataLoader] Reading {fname} ({pfile.num_row_groups} row groups, {pfile.metadata.num_rows:,} rows)...")
        
        for rg_idx in range(pfile.num_row_groups):
            df_rg = pfile.read_row_group(rg_idx).to_pandas()
            if label_col in df_rg.columns:
                df_rg['Label'] = df_rg[label_col].apply(clean_label)
                if label_col != 'Label':
                    df_rg.drop(columns=[label_col], inplace=True)
            
            # Group by class in this row group
            for cls_name, group in df_rg.groupby('Label'):
                if cls_name in class_pools:
                    class_pools[cls_name].append(group)
                else:
                    print(f"Warning: Unknown label '{cls_name}' encountered.")
                    
            del df_rg
            gc.collect()

    print("[DataLoader] Concatenating and sampling class pools...")
    sampled_dfs = []
    
    total_retained_counts = {}
    for cls_name in CANONICAL_CLASSES:
        pool_list = class_pools[cls_name]
        if not pool_list:
            print(f"Warning: No samples found for class '{cls_name}'")
            continue
        
        df_cls = pd.concat(pool_list, ignore_index=True)
        num_avail = len(df_cls)
        
        # Sampling rule:
        # If class has <= MAX_SAMPLES_PER_MAJOR_CLASS: KEEP 100% (Preserves rare attacks)
        # If class is volumetric (> MAX_SAMPLES_PER_MAJOR_CLASS): sample MAX_SAMPLES_PER_MAJOR_CLASS
        if num_avail <= MAX_SAMPLES_PER_MAJOR_CLASS:
            sampled_dfs.append(df_cls)
            total_retained_counts[cls_name] = num_avail
        else:
            df_sub = df_cls.sample(n=MAX_SAMPLES_PER_MAJOR_CLASS, random_state=random_state)
            sampled_dfs.append(df_sub)
            total_retained_counts[cls_name] = MAX_SAMPLES_PER_MAJOR_CLASS
            
        del df_cls
        gc.collect()
        
    full_sampled_df = pd.concat(sampled_dfs, ignore_index=True).sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    
    print(f"\n[DataLoader] Sampled Dataset Built: {len(full_sampled_df):,} rows, {len(full_sampled_df.columns)} columns")
    print("[DataLoader] Sampled Class Distribution:")
    for cls_name, cnt in sorted(total_retained_counts.items(), key=lambda x: -x[1]):
        print(f"  - {cls_name:30s}: {cnt:6,d} ({cnt/len(full_sampled_df)*100:5.2f}%)")
        
    return full_sampled_df

def prepare_splits(df, test_size=0.15, val_size=0.15, random_state=42):
    """
    Stratified Train (70%) / Validation (15%) / Test (15%) Split.
    Guarantees that rare attacks are represented in all splits.
    """
    print("\n[DataLoader] Performing Stratified Train / Val / Test split...")
    
    # For ultra-rare classes with very few samples (like Heartbleed: 11, SQLi: 21, Infiltration: 36),
    # ensure stratified split works cleanly
    y = df['Label']
    X = df.drop(columns=['Label'])
    
    # First split off test set (15%)
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    # Next split train and val from train_val (relative val_size is 0.15 / (1.0 - 0.15) = 0.17647)
    val_ratio = val_size / (1.0 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=val_ratio, random_state=random_state, stratify=y_train_val
    )
    
    train_df = pd.concat([X_train, y_train], axis=1).reset_index(drop=True)
    val_df = pd.concat([X_val, y_val], axis=1).reset_index(drop=True)
    test_df = pd.concat([X_test, y_test], axis=1).reset_index(drop=True)
    
    print(f"[DataLoader] Train split: {len(train_df):,} rows")
    print(f"[DataLoader] Val split:   {len(val_df):,} rows")
    print(f"[DataLoader] Test split:  {len(test_df):,} rows (UNSEEN)")
    
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    train_path = os.path.join(PROCESSED_DIR, "train.parquet")
    val_path = os.path.join(PROCESSED_DIR, "val.parquet")
    test_path = os.path.join(PROCESSED_DIR, "test.parquet")
    
    train_df.to_parquet(train_path, index=False)
    val_df.to_parquet(val_path, index=False)
    test_df.to_parquet(test_path, index=False)
    print(f"[DataLoader] Saved splits to {PROCESSED_DIR}")
    
    # Also save a sample CSV for user testing and API demonstration (e.g. 500 flows from test set)
    sample_test_csv = os.path.join(PROCESSED_DIR, "sample_traffic_test.csv")
    sample_df = test_df.sample(n=min(500, len(test_df)), random_state=random_state)
    sample_df.to_csv(sample_test_csv, index=False)
    print(f"[DataLoader] Saved test demonstration CSV ({len(sample_df)} rows) to {sample_test_csv}")
    
    return train_df, val_df, test_df

if __name__ == "__main__":
    df = load_and_sample_dataset()
    train_df, val_df, test_df = prepare_splits(df)
