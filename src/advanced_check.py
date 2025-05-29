import pandas as pd
import numpy as np
from typing import Dict, List
from data_quality_base import DataQualityCheck
from constants import EXCHANGE_NAME_COLUMN_NAME, DATE_COLUMN_NAME, VALUE_COLUMN_NAME


class AdvancedCheck(DataQualityCheck):
    """
    Advanced data quality checks for a DataFrame.
    This class performs checks for:
    - Outliers using Z-score and IQR methods
    - High correlation between numeric columns
    - Rolling outliers in time series data
    Inherits from DataQualityCheck base class.
    Inputs:
    - data: pd.DataFrame to check
    - zscore_threshold: threshold for Z-score outlier detection (default is 3.0)
    - correlation_threshold: threshold for high correlation detection (default is 0.8)
    - std_threshold: threshold for rolling outlier detection (default is 2.0)
    """

    def __init__(
        self,
        data: pd.DataFrame,
        zscore_threshold: float = 3.0,
        correlation_threshold: float = 0.8,
        std_threshold: float = 2.0,
    ):
        """
        Initializes the AdvancedCheck with a DataFrame and optional parameters for thresholds.
        """
        self.data = data
        self.zscore_threshold = zscore_threshold
        self.correlation_threshold = correlation_threshold
        self.std_threshold = std_threshold
        self.issues = {}

    def run_check(self):
        """
        Run the advanced data quality checks on the DataFrame.
        This method checks for outliers using IQR method,
        high correlation between numeric columns, and rolling outliers in time series data.
        Returns:
            Dict[str, Dict[str, pd.DataFrame]]: A dictionary containing the issues found, with keys for each check type.
        """

        self._check_outliers_iqr()

        self._check_high_correlation()

        self._check_rolling_outliers()

        return self.issues

    def _check_outliers_zscore(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Check for outliers in numeric columns using Z-score method.
        This method groups the DataFrame by 'ExchangeName' and calculates Z-scores for each numeric column.
        If the Z-score exceeds the specified threshold, the row is considered an outlier.
        """

        numeric_cols = self.data.select_dtypes(include=[np.number]).columns

        if EXCHANGE_NAME_COLUMN_NAME not in self.data.columns:
            raise ValueError(
                f"DataFrame must contain the column '{EXCHANGE_NAME_COLUMN_NAME}' for grouping."
            )

        grouped = self.data.groupby("ExchangeName")

        for col in numeric_cols:
            outlier_rows = []
            for name, group in grouped:
                series = group[col]
                if series.std(ddof=0) == 0:
                    continue  # Avoid division by zero
                z_scores = (series - series.mean()) / series.std(ddof=0)
                outliers = group[np.abs(z_scores) > self.zscore_threshold]
                if not outliers.empty:
                    outlier_rows.append(outliers)
            if outlier_rows:
                all_outliers = pd.concat(outlier_rows, axis=0)
                self.issues.setdefault("outlier_check_zscore", {})[col] = all_outliers

    def _check_outliers_iqr(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Check for outliers in numeric columns using IQR method.
        This method groups the DataFrame by 'ExchangeName' and calculates the IQR for each numeric column.
        If a value is below Q1 - 1.5 * IQR or above Q3 + 1.5 * IQR, it is considered an outlier.
        """
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns

        if EXCHANGE_NAME_COLUMN_NAME not in self.data.columns:
            raise ValueError(
                f"DataFrame must contain the column '{EXCHANGE_NAME_COLUMN_NAME}' for grouping."
            )

        grouped = self.data.groupby("ExchangeName")

        for col in numeric_cols:
            outlier_rows = []
            for name, group in grouped:
                q1 = group[col].quantile(0.25)
                q3 = group[col].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                outliers = group[(group[col] < lower_bound) | (group[col] > upper_bound)]
                if not outliers.empty:
                    outlier_rows.append(outliers)
            if outlier_rows:
                all_outliers = pd.concat(outlier_rows, axis=0)
                self.issues.setdefault("outlier_check_iqr", {})[col] = all_outliers

    def _check_high_correlation(self):
        """
        Check for high correlation between numeric columns in the DataFrame.
        This method calculates the absolute correlation matrix for numeric columns,
        identifies pairs of columns with correlation above the specified threshold,
        and stores the pairs in the issues dictionary.
        """
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        numeric_df = self.data[numeric_cols]
        if numeric_df.empty:
            raise ValueError("DataFrame must contain numeric columns for correlation checks.")
        corr_matrix = numeric_df.corr().abs()
        upper_triangle = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))

        correlated_pairs = []
        for i, col1 in enumerate(corr_matrix.columns):
            for j in range(i + 1, len(corr_matrix.columns)):
                col2 = corr_matrix.columns[j]
                corr_value = corr_matrix.iloc[i, j]
                if corr_value > self.correlation_threshold:
                    pair_desc = f"{col1} & {col2}: correlation = {corr_value:.2f}"
                    correlated_pairs.append(pair_desc)

        if correlated_pairs:
            key = "high_correlation"
            self.issues.setdefault("high_correlation", {})[key] = correlated_pairs
        else:
            self.issues.setdefault("high_correlation", {})[
                "message"
            ] = "No pairs with high correlation found."

    def _check_rolling_outliers(self, window: int = 3):
        """
        Check for rolling outliers in time series data.
        This method calculates the rolling mean and standard deviation for each exchange's value column,
        and identifies outliers based on the specified standard deviation threshold.
        """
        if (
            DATE_COLUMN_NAME not in self.data.columns
            or VALUE_COLUMN_NAME not in self.data.columns
            or EXCHANGE_NAME_COLUMN_NAME not in self.data.columns
        ):
            raise ValueError(
                f"DataFrame must contain the columns '{DATE_COLUMN_NAME}', '{VALUE_COLUMN_NAME}', and '{EXCHANGE_NAME_COLUMN_NAME}' for rolling checks."
            )

        df_sorted = self.data.sort_values(by=[EXCHANGE_NAME_COLUMN_NAME, DATE_COLUMN_NAME])
        rolling_mean = df_sorted.groupby(EXCHANGE_NAME_COLUMN_NAME)[VALUE_COLUMN_NAME].transform(
            lambda x: x.rolling(window=window, min_periods=1).mean()
        )
        rolling_std = df_sorted.groupby(EXCHANGE_NAME_COLUMN_NAME)[VALUE_COLUMN_NAME].transform(
            lambda x: x.rolling(window=window, min_periods=1).std()
        )

        deviation = (df_sorted[VALUE_COLUMN_NAME] - rolling_mean).abs()
        outliers_mask = deviation > self.std_threshold * rolling_std

        # issues = []
        # for group, group_df in df_sorted.groupby(EXCHANGE_NAME_COLUMN_NAME):
        #     outlier_indices = group_df.index[outliers.loc[group_df.index]].tolist()
        #     if outlier_indices:
        #         self.issues.setdefault("rolling_outlier_check", {})[VALUE_COLUMN_NAME] = outliers
        outlier_rows = df_sorted[outliers_mask]
        if not outlier_rows.empty:
            self.issues.setdefault("rolling_outliers", {})[VALUE_COLUMN_NAME] = outlier_rows

    def summarize_issues(self):
        """
        Summarizes the issues found during the checks in a dictionary format.
        """
        if not self.issues:
            print("No issues found.")
            return None
        summary = {}

        for check_name, column_issues in self.issues.items():
            summary[check_name] = {}
            for column, df in column_issues.items():
                summary[check_name][column] = {}
                if isinstance(df, pd.DataFrame) and EXCHANGE_NAME_COLUMN_NAME in df.columns:
                    for exch, group in df.groupby(EXCHANGE_NAME_COLUMN_NAME):
                        summary[check_name][column][exch] = {
                            "num_issues": f"{len(group)} issues found out of {len(self.data[self.data[EXCHANGE_NAME_COLUMN_NAME]==exch])} total rows"
                        }
                else:
                    summary[check_name][column]["all"] = {
                        "num_issues": f"{len(df) if hasattr(df, '__len__') else 1} issues found"
                    }
        return summary

    def save_issues(self, file_path: str) -> None:
        """
        Saves the issues to a specified file path.
        """
        summary = self.summarize_issues()
        if not summary:
            print("No issues to save.")
            return
        with open(file_path, "w") as f:
            for check_name, column_issues in summary.items():
                f.write(f"Check: {check_name}\n")
                for column, issue_info in column_issues.items():
                    f.write(f"  Column: {column}\n")
                    if isinstance(issue_info, dict):
                        for exch, issue in issue_info.items():
                            f.write(f"    Exchange: {exch}\n")
                            f.write(f"      Issues: {issue['num_issues']}\n")
