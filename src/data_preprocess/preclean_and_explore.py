import pandas as pd
from abc import ABC, abstractmethod
from typing import Optional
from pathlib import Path

from constants import (
    CLEANED_COLUMN_NAMES,
    EXCHANGE_NAME_COLUMN_NAME,
    MIC_COLUMN_NAME,
    OPERATING_MIC_COLUMN_NAME,
    CURRENCY_CODE_COLUMN_NAME,
    CURRENCY_COLUMN_NAME,
    CURRENCY_NAME_COLUMN_NAME,
    ALPHABETIC_CODE_COLUMN_NAME,
    MARKET_NAME_INSTITUTION_DESCRIPTION_COLUMN_NAME,
    YEAR_COLUMN_NAME,
    MONTH_COLUMN_NAME,
    OPEN_COLUMN_NAME,
    HIGH_COLUMN_NAME,
    LOW_COLUMN_NAME,
    CLOSE_COLUMN_NAME,
    DATE_COLUMN_NAME,
    VIX_DATE_COLUMN_NAME,
    VIX_FILE_PATH,
    MIC_FILE_PATH,
    CURRENCY_CODE_FILE_PATH,
    VALUE_COLUMN_NAME,
    MTM_PCT_COLUMN_NAME,
    YTY_PCT_COLUMN_NAME,
    ANNUAL_VALUE_COLUMN_NAME,
    CLEANED_DATASET_FILE_PATH,
    AVG_MTM_PCT_COLUMN_NAME,
    AVG_YTY_PCT_COLUMN_NAME,
)


class BasePreprocessor(ABC):
    """
    An abstract base class for dataset preprocessing.
    It defines the structure for loading data and precleaning datasets.
    Inputs:
        filepath (str): The file path to the dataset.
        df (Optional[pd.DataFrame]): DataFrame to hold the loaded data.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.df: Optional[pd.DataFrame] = None

    @abstractmethod
    def load_data(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def preclean_and_save_dataset(self) -> pd.DataFrame:
        pass


class BaseExplorer(ABC):
    """
    An abstract base class for dataset exploration.
    It defines the structure for exploring datasets.
    Inputs:
        df (pd.DataFrame): The DataFrame to explore.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df

    @abstractmethod
    def explore(self):
        pass


class DatasetPreprocessor(BasePreprocessor):
    """
    A class to preprocess and merge datasets from multiple file paths.
    It loads data from CSV and Excel files, merges them with MIC, currency, and VIX data,
    calculates MTM and YTY changes, and saves the cleaned dataset to a specified output path.
    It inherits from the BasePreprocessor abstract class.

    Inputs:
        filepaths (list[str]): List of file paths to load data from.
        df (Optional[pd.DataFrame]): DataFrame to hold the loaded and processed data.
    """

    def __init__(self, filepaths: list[str]):
        """
        Initializes the DatasetPreprocessor with a list of file paths.
        """
        self.filepaths = filepaths
        self.df: Optional[pd.DataFrame] = None

    @staticmethod
    def _load_file(path: Path) -> pd.DataFrame:
        """
        Load a file based on its extension.
        This method supports CSV and Excel files (.xlsx, .xls).
        """
        print(f"Loading file: {path}")
        if path.suffix == ".csv":
            return pd.read_csv(path)
        elif path.suffix == ".xlsx":
            return pd.read_excel(path, engine="openpyxl")
        elif path.suffix == ".xls":
            return pd.read_excel(path, engine="xlrd")
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")

    def load_data(self) -> pd.DataFrame:
        """
        Load data from multiple file paths and concatenate them into a single DataFrame.
        This method handles loading CSV and Excel files, and concatenates them into a single DataFrame.
        """
        dfs = []
        for path in self.filepaths:
            dfs.append(self._load_file(path))
        self.df = pd.concat(dfs, ignore_index=True) if dfs else None
        print(
            f"Data loaded successfully, shape: {self.df.shape if self.df is not None else 'None'}"
        )
        return self.df

    def _merge_mic(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge the DataFrame with MIC data based on exchange names.
        This method loads the MIC data, cleans the exchange names, and merges it with the main DataFrame.
        """
        mic_df = self._load_file(MIC_FILE_PATH)
        df[EXCHANGE_NAME_COLUMN_NAME] = df[EXCHANGE_NAME_COLUMN_NAME].str.strip().str.lower()
        mic_df[MARKET_NAME_INSTITUTION_DESCRIPTION_COLUMN_NAME] = (
            mic_df[MARKET_NAME_INSTITUTION_DESCRIPTION_COLUMN_NAME].str.strip().str.lower()
        )

        return df.merge(
            mic_df[
                [
                    MARKET_NAME_INSTITUTION_DESCRIPTION_COLUMN_NAME,
                    MIC_COLUMN_NAME,
                    OPERATING_MIC_COLUMN_NAME,
                ]
            ],
            left_on=EXCHANGE_NAME_COLUMN_NAME,
            right_on=MARKET_NAME_INSTITUTION_DESCRIPTION_COLUMN_NAME,
            how="left",
        )

    def _merge_currency(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge the DataFrame with currency code data based on currency names.
        This method loads the currency code data, cleans the currency names, and merges it with the main DataFrame.
        """
        currency_code_df = self._load_file(CURRENCY_CODE_FILE_PATH)
        df[CURRENCY_NAME_COLUMN_NAME] = df[CURRENCY_NAME_COLUMN_NAME].str.strip().str.lower()
        currency_code_df[CURRENCY_COLUMN_NAME] = (
            currency_code_df[CURRENCY_COLUMN_NAME].str.strip().str.lower()
        )
        currency_code_unique = currency_code_df.drop_duplicates(
            subset=[CURRENCY_COLUMN_NAME], keep="first"
        )
        return df.merge(
            currency_code_unique[[CURRENCY_COLUMN_NAME, ALPHABETIC_CODE_COLUMN_NAME]],
            left_on=CURRENCY_NAME_COLUMN_NAME,
            right_on=CURRENCY_COLUMN_NAME,
            how="left",
        )

    def _merge_vix(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge the DataFrame with VIX data based on year and month.
        This method loads the VIX data, resamples it to monthly frequency, and merges it with the main DataFrame.
        """
        vix_df = self._load_file(VIX_FILE_PATH)
        vix_df[VIX_DATE_COLUMN_NAME] = pd.to_datetime(vix_df[VIX_DATE_COLUMN_NAME])
        vix_df.set_index(VIX_DATE_COLUMN_NAME, inplace=True)
        vix_monthly = (
            vix_df.resample("ME")
            .agg(
                {
                    OPEN_COLUMN_NAME: "first",
                    HIGH_COLUMN_NAME: "max",
                    LOW_COLUMN_NAME: "min",
                    CLOSE_COLUMN_NAME: "last",
                }
            )
            .reset_index()
        )
        vix_monthly[YEAR_COLUMN_NAME] = vix_monthly[VIX_DATE_COLUMN_NAME].dt.year
        vix_monthly[MONTH_COLUMN_NAME] = vix_monthly[VIX_DATE_COLUMN_NAME].dt.strftime("%b")
        df = df.merge(
            vix_monthly[
                [
                    YEAR_COLUMN_NAME,
                    MONTH_COLUMN_NAME,
                    OPEN_COLUMN_NAME,
                    HIGH_COLUMN_NAME,
                    LOW_COLUMN_NAME,
                    CLOSE_COLUMN_NAME,
                ]
            ],
            on=[YEAR_COLUMN_NAME, MONTH_COLUMN_NAME],
            how="left",
        )
        df[DATE_COLUMN_NAME] = pd.to_datetime(
            df[YEAR_COLUMN_NAME].astype(str) + "-" + df[MONTH_COLUMN_NAME],
            format="%Y-%b",
            errors="coerce",
        )
        return df

    def merge_dataset(self) -> pd.DataFrame:
        """
        Merge the dataset by loading data from multiple file paths and merging with MIC, currency, and VIX data.
        This method loads the data, merges it with MIC, currency, and VIX data, and returns the final DataFrame.
        """
        df = self.load_data()
        df = self._merge_mic(df)
        df = self._merge_currency(df)
        df = self._merge_vix(df)
        return df

    def calculate_mtm_change(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the Month-to-Month (MTM) percentage change for each exchange.
        This method sorts the DataFrame by exchange name and date, calculates the percentage change,
        and adds a new column for MTM percentage change.
        """
        df = df.sort_values(by=[EXCHANGE_NAME_COLUMN_NAME, DATE_COLUMN_NAME])
        df[MTM_PCT_COLUMN_NAME] = (
            df.groupby([EXCHANGE_NAME_COLUMN_NAME])[VALUE_COLUMN_NAME]
            .transform(lambda x: x.pct_change() * 100)
            .round(2)
        )

        df[MTM_PCT_COLUMN_NAME] = df[MTM_PCT_COLUMN_NAME].replace(float("inf"), 100)
        df[MTM_PCT_COLUMN_NAME] = df[MTM_PCT_COLUMN_NAME].replace(float("-inf"), -100)
        return df

    def calculate_yty_change(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the Year-to-Year (YTY) percentage change for each exchange.
        This method groups the DataFrame by year and exchange name, calculates the annual sum,
        and computes the percentage change for each exchange.
        """
        annual = (
            df.groupby([YEAR_COLUMN_NAME, EXCHANGE_NAME_COLUMN_NAME], as_index=False)[
                VALUE_COLUMN_NAME
            ]
            .sum()
            .rename(columns={VALUE_COLUMN_NAME: ANNUAL_VALUE_COLUMN_NAME})
        )
        annual = annual.sort_values([EXCHANGE_NAME_COLUMN_NAME, YEAR_COLUMN_NAME])
        annual[YTY_PCT_COLUMN_NAME] = (
            annual.groupby([EXCHANGE_NAME_COLUMN_NAME])[ANNUAL_VALUE_COLUMN_NAME]
            .transform(lambda x: x.pct_change() * 100)
            .round(2)
        )

        annual[YTY_PCT_COLUMN_NAME] = annual[YTY_PCT_COLUMN_NAME].replace(float("inf"), 100)
        annual[YTY_PCT_COLUMN_NAME] = annual[YTY_PCT_COLUMN_NAME].replace(float("-inf"), -100)

        # Merge the YTY percentage back to df
        df = df.merge(
            annual[[YEAR_COLUMN_NAME, EXCHANGE_NAME_COLUMN_NAME, YTY_PCT_COLUMN_NAME]],
            on=[YEAR_COLUMN_NAME, EXCHANGE_NAME_COLUMN_NAME],
            how="left",
        )
        return df

    def convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert columns in the DataFrame to numeric types where applicable.
        This method attempts to convert object columns to numeric types, handling any conversion errors.
        """
        for col in df.columns:
            try:
                if df[col].dtype == object:
                    df[col] = pd.to_numeric(df[col])
            except ValueError:
                print(f"Column {col} could not be converted to numeric, keeping as is.")
        return df

    def preclean_and_save_dataset(self, output_path: Path) -> pd.DataFrame:
        """
        Preprocess the dataset by merging, cleaning, and calculating changes.
        This method loads the dataset, merges it with MIC, currency, and VIX data,
        calculates MTM and YTY changes, renames columns, and saves the cleaned dataset to a specified output path.
        Inputs:
            output_path (Path): The file path to save the cleaned dataset.
        """
        print("Preprocessing dataset...")
        df = self.merge_dataset()
        print(f"Dataset loaded and merged successfully, shape: {df.shape}")

        df = df.drop_duplicates()

        print(f"Duplicates removed, new shape: {df.shape}")

        ## There are two weird rows so we drop them
        df = df[~df[DATE_COLUMN_NAME].isnull()].reset_index(drop=True)

        df = df.rename(columns={ALPHABETIC_CODE_COLUMN_NAME: CURRENCY_CODE_COLUMN_NAME})
        df = self.convert_data_types(df)

        df = self.calculate_mtm_change(df)
        df = self.calculate_yty_change(df)

        print(f"MTM and YTY changes calculated, new shape: {df.shape}")

        df = df[CLEANED_COLUMN_NAMES]

        print(f"Columns renamed and selected, new shape: {df.shape}")

        df.to_csv(output_path, index=False)

        self.df = df


class DatasetExplorer(BaseExplorer):
    """
    A class to explore and analyze a dataset.
    It provides methods to display basic statistics, unique values in categorical columns,
    and the first few rows of the DataFrame.

    It inherits from the BaseExplorer abstract class.
    Inputs:
        df (pd.DataFrame): The DataFrame to explore.
    """

    def explore(self):
        """
        Explore the dataset by displaying its shape, columns, data types, basic statistics,
        unique values in categorical columns, and the first few rows.
        This method prints the shape of the DataFrame, the columns it contains, their data types,
        basic statistics, unique values in categorical columns, and the first few rows of the DataFrame.
        """
        print("Exploring dataset...")
        print(f"Shape of the DataFrame: {self.df.shape}")
        print(f"Columns in the DataFrame: {self.df.columns.tolist()}")
        print(f"Data types of columns:\n{self.df.dtypes}")

        # Display basic statistics
        print("Basic statistics:")
        print(self.df.describe(include="all"))

        # Display unique values in categorical columns
        for col in self.df.select_dtypes(include=["object"]).columns:
            print(f"Unique values in '{col}': {self.df[col].nunique()}")

        # Display first few rows
        print("First few rows of the DataFrame:")
        print(self.df.head())

    def identify_top_n_growing_market_MTM_pct_all_indicators(self, n: int = 10):
        """
        Identify the top N growing markets based on Month-to-Month (MTM) percentage change.
        This method groups the DataFrame by exchange name, calculates the average MTM percentage change,
        and sorts the results to identify the top N growing markets.
        """

        print(f"Identifying top {n} growing markets based on MTM pct including all indicators...")
        exchange_growth = (
            self.df.groupby(EXCHANGE_NAME_COLUMN_NAME)[MTM_PCT_COLUMN_NAME]
            .mean()
            .reset_index(name=AVG_MTM_PCT_COLUMN_NAME)
            .sort_values(AVG_MTM_PCT_COLUMN_NAME, ascending=False)
        )
        top10 = exchange_growth.sort_values(AVG_MTM_PCT_COLUMN_NAME, ascending=False).head(n)
        print(top10)

    def identify_top_n_growing_market_YTY_pct_all_indicators(self, n: int = 10):
        """
        Identify the top N growing markets based on Year-to-Year (YTY) percentage change.
        This method groups the DataFrame by exchange name, calculates the average YTY percentage change,
        and sorts the results to identify the top N growing markets.
        """
        print(f"Identifying top {n} growing markets based on YTY pct including all indicators...")
        exchange_growth = (
            self.df.groupby(EXCHANGE_NAME_COLUMN_NAME)[YTY_PCT_COLUMN_NAME]
            .mean()
            .reset_index(name=AVG_YTY_PCT_COLUMN_NAME)
            .sort_values(AVG_YTY_PCT_COLUMN_NAME, ascending=False)
        )
        top10 = exchange_growth.sort_values(AVG_YTY_PCT_COLUMN_NAME, ascending=False).head(n)
        print(top10)
