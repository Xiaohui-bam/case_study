import pandas as pd
from typing import Dict
from .data_quality_base import DataQualityCheck
from constants import (
    NEGATIVE_CHECK_COLUMN_NAMES,
    STRING_LENGTH_CHECK_COLUMN_NAMES,
    EXPECTED_DTYPE,
)


class BasicCheck(DataQualityCheck):
    """
    Basic data quality checks for a DataFrame.
    Checks for:
    - Missing values
    - Negative values in specified columns
    - String length exceeding a specified maximum
    - Data type mismatches
    - Duplicate rows

    Inherits from DataQualityCheck base class.

    Inputs:
    - data: pd.DataFrame to check
    - expected_dtypes: dict of column -> expected dtype (e.g. {'value': 'float', 'exchange_code': 'object'})
    - max_str_length: maximum length for string columns (default is 100)
    """

    def __init__(
        self, data: pd.DataFrame, expected_dtypes: dict = EXPECTED_DTYPE, max_str_length: int = 100
    ):
        """
        Initializes the BasicCheck with a DataFrame and optional parameters for expected dtypes and max string length.
        """
        self.data = data
        self.expected_dtypes = expected_dtypes or {}
        self.max_str_length = max_str_length

    def run_check(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Run the basic data quality checks on the DataFrame.
        This method checks for missing values, negative values in specified columns,
        string length exceeding a specified maximum, data type mismatches, and duplicate rows.
        Returns:
            Dict[str, Dict[str, pd.DataFrame]]: A dictionary containing the issues found, with keys for each check type.
        """
        self.issues = {}
        self._check_duplicates()
        self._check_missing_values()
        self._check_negative_values()
        self._check_string_length()
        self._check_dtypes()
        return self.issues

    def _check_missing_values(self):
        """
        Check for missing values in the DataFrame.
        """

        for col in self.data.columns:
            missing = self.data[self.data[col].isnull()]
            if not missing.empty:
                self.issues.setdefault("missing_values", {})[col] = missing

    def _check_negative_values(self):
        """
        Check for negative values in specified columns.
        """
        for col in NEGATIVE_CHECK_COLUMN_NAMES:
            if col in self.data.columns and pd.api.types.is_numeric_dtype(self.data[col]):
                negative_vals = self.data[self.data[col] < 0]
                if not negative_vals.empty:
                    self.issues.setdefault("negative_values", {})[col] = negative_vals

    def _check_string_length(self):
        """
        Check for string length exceeding a specified maximum in specified columns.
        """
        for col in STRING_LENGTH_CHECK_COLUMN_NAMES:
            if col in self.data.columns and pd.api.types.is_string_dtype(self.data[col]):
                too_long = self.data[self.data[col].str.len() > self.max_str_length]
                if not too_long.empty:
                    self.issues.setdefault("string_length_exceeded", {})[col] = too_long

    def _check_dtypes(self):
        """
        Check for data type mismatches in specified columns.
        """
        for col, expected_dtype in self.expected_dtypes.items():
            if col in self.data.columns:
                actual_dtype = str(self.data[col].dtype)
                if actual_dtype != expected_dtype:
                    dtype_mismatch = self.data[[col]]
                    dtype_mismatch["expected_dtype"] = expected_dtype
                    dtype_mismatch["actual_dtype"] = actual_dtype
                    self.issues.setdefault("dtype_mismatch", {})[col] = dtype_mismatch

    def _check_duplicates(self):
        """
        Check for duplicate rows in the DataFrame.
        """
        duplicate_rows = self.data[self.data.duplicated()]
        if not duplicate_rows.empty:
            self.issues.setdefault("duplicate_rows", {})["all_column_duplicates"] = duplicate_rows
