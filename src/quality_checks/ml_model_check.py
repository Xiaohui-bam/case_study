import pandas as pd
from sklearn.ensemble import IsolationForest

from .advanced_check import AdvancedCheck
from constants import EXCHANGE_NAME_COLUMN_NAME, VALUE_COLUMN_NAME


class MachineLearningCheck(AdvancedCheck):
    """
    Machine Learning-based data quality checks for a DataFrame.
    This class performs anomaly detection using Isolation Forest.
    Inherits from AdvancedCheck class.
    Inputs:
    - data: pd.DataFrame to check
    - contamination: proportion of outliers in the data (default is 0.01)
    """

    def __init__(self, data: pd.DataFrame, contamination: float = 0.01):
        """
        Initializes the MachineLearningCheck with a DataFrame and optional contamination parameter.
        """
        self.data = data
        self.contamination = contamination
        self.issues = {}

    def run_check(self):
        """
        Run the machine learning-based data quality checks on the DataFrame.
        This method checks for anomalies using Isolation Forest.
        Returns:
            Dict[str, Dict[str, pd.DataFrame]]: A dictionary containing the issues found, with keys for each check type.
        """
        self._check_anomalies_with_isolation_forest()
        return self.issues

    def _check_anomalies_with_isolation_forest(self):
        """
        Check for anomalies in the DataFrame using Isolation Forest.
        This method groups the DataFrame by 'ExchangeName' and applies Isolation Forest to detect anomalies
        in the specified value column.

        """

        grouped = self.data.groupby(EXCHANGE_NAME_COLUMN_NAME)
        if VALUE_COLUMN_NAME not in self.data.columns:
            raise ValueError(
                f"DataFrame must contain the column '{VALUE_COLUMN_NAME}' for anomaly detection."
            )
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
