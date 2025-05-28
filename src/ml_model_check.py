from sklearn.ensemble import IsolationForest
import pandas as pd
import numpy as np

from src.advanced_check import AdvancedCheck
from src.constants import EXCHANGE_NAME_COLUMN_NAME, VALUE_COLUMN_NAME

class MachineLearningCheck(AdvancedCheck):
    def __init__(self, data: pd.DataFrame, contamination: float = 0.01):
        self.data = data
        self.contamination = contamination
        self.issues = {}

    def run_check(self):
        self._check_anomalies_with_isolation_forest()

    def _check_anomalies_with_isolation_forest(self):

        grouped = self.data.groupby(EXCHANGE_NAME_COLUMN_NAME)
        if VALUE_COLUMN_NAME not in self.data.columns:
            raise ValueError(f"DataFrame must contain the column '{VALUE_COLUMN_NAME}' for anomaly detection.")
        outlier_rows = []
        for exch, group in grouped:
            clean_series = group[VALUE_COLUMN_NAME].dropna()
            if clean_series.empty:
                continue

            model = IsolationForest(contamination=self.contamination, random_state=42)
            preds = model.fit_predict(clean_series.values.reshape(-1, 1))
            anomaly_indices = clean_series.index[preds == -1]

            if len(anomaly_indices) > 0:
                anomaly_df = group.loc[anomaly_indices]
                outlier_rows.append(anomaly_df)
        if outlier_rows:
            all_outliers = pd.concat(outlier_rows, axis=0)
            self.issues.setdefault("isolation_forest_anomaly", {})[VALUE_COLUMN_NAME] = all_outliers