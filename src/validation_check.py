import re
import pandas as pd
from typing import Dict
from data_quality_base import DataQualityCheck
from constants import MIC_COLUMN_NAME, CURRENCY_CODE_COLUMN_NAME


class ValidationCheck(DataQualityCheck):
    """
    Class for performing validation checks on the DataFrame.
    This class checks the format of Market Identifier Codes (MICs) and ISO 4217 currency codes.
    It inherits from the DataQualityCheck base class.
    Inputs:
        data (pd.DataFrame): The DataFrame to be checked.
    """

    def run_check(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Run the validation checks on the DataFrame.
        This method checks the format of MICs and currency codes, and returns a dictionary of issues found.
        Returns:
            Dict[str, Dict[str, pd.DataFrame]]: A dictionary containing the issues found, with keys for each check type.
        """
        self.issues = {}
        self._check_mic_format()
        self._check_currency_code_format()
        return self.issues

    def _check_mic_format(self):
        """
        Check if the 'mic' column contains valid Market Identifier Codes (MICs).
        A valid MIC is a 4 digit alphanumeric code.
        """

        if MIC_COLUMN_NAME in self.data.columns:
            invalid = self.data[
                ~self.data[MIC_COLUMN_NAME].astype(str).str.match(r"^[A-Za-z0-9]{4}$", na=False)
            ]
            if not invalid.empty:
                self.issues.setdefault("mic_format_check", {})[MIC_COLUMN_NAME] = invalid

        else:
            raise ValueError(f"Column '{MIC_COLUMN_NAME}' not found in the DataFrame.")

    def _check_currency_code_format(self):
        """
        Check if the 'currency_code' column contains valid ISO 4217 currency codes.
        A valid currency code is a 3 letter uppercase code.
        """

        if CURRENCY_CODE_COLUMN_NAME in self.data.columns:
            invalid = self.data[
                ~self.data[CURRENCY_CODE_COLUMN_NAME].astype(str).str.match(r"^[A-Z]{3}$", na=False)
            ]
            if not invalid.empty:
                self.issues.setdefault("currency_code_format_check", {})[
                    CURRENCY_CODE_COLUMN_NAME
                ] = invalid
        else:
            raise ValueError(f"Column '{CURRENCY_CODE_COLUMN_NAME}' not found in the DataFrame.")
