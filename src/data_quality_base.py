from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any

class DataQualityCheck(ABC):
    """
    Abstract base class for all grouped data quality check classes (e.g., BasicChecks, AdvancedChecks).
    Each concrete class should implement the run_check() method and optionally expose internal checks.

    Inputs:
        data (pd.DataFrame): The DataFrame to be checked.
    """

    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.issues: Dict[str, Any] = {}

    @abstractmethod
    def run_check(self) -> Dict[str, pd.DataFrame]:
        """
        Runs all relevant checks and stores results in `self.issues`.
        Should return a dictionary of issue DataFrames.
        """
        pass

    def get_issues(self) -> Dict[str, pd.DataFrame]:
        """
        Returns all issues identified by the check.
        """
        return self.issues

    def summarize_issues(self) -> None:
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
                summary[check_name][column] = {
                    "num_issues": f"{len(df)} issues found out of {len(self.data)} total rows",
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
        with open(file_path, 'w') as f:
            for check_name, column_issues in summary.items():
                f.write(f"Check: {check_name}\n")
                for column, issue_info in column_issues.items():
                    f.write(f"  Column: {column}\n")
                    f.write(f"    Issues: {issue_info['num_issues']}\n")
    
    def export_issues_to_xlsx(self, file_path: str) -> None:
        """
        Exports the issues to a XLSX file.
        """
        with pd.ExcelWriter(file_path) as writer:
            for check_name, column_issues in self.issues.items():
                for column, df in column_issues.items():
                    if isinstance(df, pd.DataFrame):
                        sheet_name = f"{check_name}_{column}"[:31]  # Excel sheet name max length is 31
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                    else:
                        # If not a DataFrame, write as a summary DataFrame
                        pd.DataFrame({"issue": [df]}).to_excel(writer, sheet_name=f"{check_name}_{column}"[:31], index=False)