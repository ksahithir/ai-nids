import os
import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import RobustScaler

# Constant features with zero variance to drop
CONSTANT_FEATURES = [
    "Bwd PSH Flags",
    "Bwd URG Flags",
    "Fwd Avg Bytes/Bulk",
    "Fwd Avg Packets/Bulk",
    "Fwd Avg Bulk Rate",
    "Bwd Avg Bytes/Bulk",
    "Bwd Avg Packets/Bulk",
    "Bwd Avg Bulk Rate"
]

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

# Threat severity definition
SEVERITY_MAPPING = {
    "Benign": "LOW",
    "PortScan": "LOW",
    "DoS GoldenEye": "MEDIUM",
    "DoS slowloris": "MEDIUM",
    "DoS Slowhttptest": "MEDIUM",
    "FTP-Patator": "MEDIUM",
    "SSH-Patator": "MEDIUM",
    "DDoS": "HIGH",
    "DoS Hulk": "HIGH",
    "Web Attack - Brute Force": "HIGH",
    "Web Attack - XSS": "HIGH",
    "Bot": "CRITICAL",
    "Infiltration": "CRITICAL",
    "Web Attack - SQL Injection": "CRITICAL",
    "Heartbleed": "CRITICAL"
}

class NIDSFeatureSelector(BaseEstimator, TransformerMixin):
    """
    Selects valid features, prunes constant columns, and handles invalid values.
    """
    def __init__(self, constant_cols=None):
        self.constant_cols = constant_cols if constant_cols is not None else CONSTANT_FEATURES
        self.feature_names_in_ = None
        self.selected_features_ = None
        self.medians_ = {}

    def fit(self, X, y=None):
        if isinstance(X, pd.DataFrame):
            self.feature_names_in_ = list(X.columns)
            self.selected_features_ = [c for c in X.columns if c not in self.constant_cols and c.lower() != 'label']
            # Calculate medians for imputation safety
            for col in self.selected_features_:
                self.medians_[col] = float(X[col].median())
        else:
            raise ValueError("Input X must be a pandas DataFrame with named columns.")
        return self

    def transform(self, X):
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X, columns=self.feature_names_in_)
        else:
            X = X.copy()

        # Ensure all selected features exist (if missing in input, fill with fitted median)
        for col in self.selected_features_:
            if col not in X.columns:
                X[col] = self.medians_.get(col, 0.0)

        # Select only the relevant features in deterministic order
        X_selected = X[self.selected_features_].copy()

        # Handle NaNs, Infs safely
        for col in self.selected_features_:
            col_series = pd.to_numeric(X_selected[col], errors='coerce')
            col_vals = np.array(col_series.values, dtype=np.float64, copy=True)
            median_val = self.medians_.get(col, 0.0)
            col_vals[np.isinf(col_vals)] = np.nan
            col_vals[np.isnan(col_vals)] = median_val
            X_selected[col] = col_vals

        return X_selected

class NIDSPreprocessor(BaseEstimator, TransformerMixin):
    """
    Complete Preprocessing Pipeline encapsulating Feature Selection and Robust Scaling.
    Fitted strictly on training data only.
    """
    def __init__(self):
        self.selector = NIDSFeatureSelector()
        self.scaler = RobustScaler()
        self.is_fitted = False

    def fit(self, X, y=None):
        X_sel = self.selector.fit_transform(X)
        self.scaler.fit(X_sel)
        self.is_fitted = True
        return self

    def transform(self, X):
        if not self.is_fitted:
            raise RuntimeError("NIDSPreprocessor must be fitted before transforming data.")
        X_sel = self.selector.transform(X)
        X_scaled = self.scaler.transform(X_sel)
        return X_scaled

    @property
    def selected_features(self):
        return self.selector.selected_features_

    @property
    def input_features(self):
        return self.selector.feature_names_in_

class NIDSLabelEncoder:
    """
    Maps the 15 canonical classes to contiguous integer IDs and vice-versa.
    """
    def __init__(self, classes=CANONICAL_CLASSES):
        self.classes = list(classes)
        self.class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
        self.idx_to_class = {idx: cls for idx, cls in enumerate(self.classes)}

    def transform(self, y):
        if isinstance(y, (pd.Series, pd.DataFrame)):
            y_list = y.tolist()
        else:
            y_list = list(y)
        return np.array([self.class_to_idx.get(lbl, 0) for lbl in y_list], dtype=int)

    def inverse_transform(self, indices):
        return [self.idx_to_class.get(idx, "Benign") for idx in indices]

def save_preprocessor(preprocessor, label_encoder, filepath="models/preprocessing_pipeline.joblib"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    payload = {
        "preprocessor": preprocessor,
        "label_encoder": label_encoder,
        "selected_features": preprocessor.selected_features,
        "classes": label_encoder.classes,
        "severity_mapping": SEVERITY_MAPPING
    }
    joblib.dump(payload, filepath)
    print(f"[Preprocessing] Saved preprocessor pipeline to {filepath}")

def load_preprocessor(filepath="models/preprocessing_pipeline.joblib"):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Preprocessor file not found at {filepath}")
    payload = joblib.load(filepath)
    return payload
