import pandas as pd
from typing import Dict
from src.data_quality_base import DataQualityCheck
from src.constants import NEGATIVE_CHECK_COLUMN_NAMES, STRING_LENGTH_CHECK_COLUMN_NAMES, EXPECTED_DTYPE

class BasicCheck(DataQualityCheck):
    def __init__(self, data: pd.DataFrame, expected_dtypes: dict = EXPECTED_DTYPE, max_str_length: int = 100):
        """
        expected_dtypes: dict of column -> expected dtype (e.g. {'value': 'float', 'exchange_code': 'object'})
        max_str_length: dict of column -> max length (for string columns)
        """
        self.data = data
        self.expected_dtypes = expected_dtypes or {}
        self.max_str_length = max_str_length

    def run_check(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        self.issues = {}
        self._check_duplicates()
        self._check_missing_values()
        self._check_negative_values()
        self._check_string_length()
        self._check_dtypes()
        return self.issues

    def _check_missing_values(self):
        for col in self.data.columns:
            missing = self.data[self.data[col].isnull()]
            if not missing.empty:
                self.issues.setdefault("missing_values", {})[col] = missing

    def _check_negative_values(self):
        for col in NEGATIVE_CHECK_COLUMN_NAMES:
            if col in self.data.columns and pd.api.types.is_numeric_dtype(self.data[col]):
                negative_vals = self.data[self.data[col] < 0]
                if not negative_vals.empty:
                    self.issues.setdefault("negative_values", {})[col] = negative_vals


    def _check_string_length(self):
        for col in STRING_LENGTH_CHECK_COLUMN_NAMES:
            if col in self.data.columns and pd.api.types.is_string_dtype(self.data[col]):
                too_long = self.data[self.data[col].str.len() > self.max_str_length]
                if not too_long.empty:
                    self.issues.setdefault("string_length_exceeded", {})[col] = too_long
    
    def _check_dtypes(self):
        for col, expected_dtype in self.expected_dtypes.items():
            if col in self.data.columns:
                actual_dtype = str(self.data[col].dtype)
                if actual_dtype != expected_dtype:
                    dtype_mismatch = self.data[[col]]
                    dtype_mismatch['expected_dtype'] = expected_dtype
                    dtype_mismatch['actual_dtype'] = actual_dtype
                    self.issues.setdefault("dtype_mismatch", {})[col] = dtype_mismatch

    def _check_duplicates(self):
        duplicate_rows = self.data[self.data.duplicated()]
        if not duplicate_rows.empty:
             self.issues.setdefault("duplicate_rows", {})["all_column_duplicates"] = duplicate_rows