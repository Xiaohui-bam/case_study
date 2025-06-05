# Constants for data processing and exploration
from pathlib import Path

DATA_FILE_PATHS = [
    Path("input/all_markets_202101_202106_481292_20240618152800.xlsx"),
    Path("input/all_markets_202107_202112_481292_20240618152800.xlsx"),
    Path("input/all_markets_202201_202206_481292_20240618152800.xlsx"),
    Path("input/all_markets_202207_202212_481292_20240618152800.xlsx"),
    Path("input/all_markets_202301_202306_481292_20240607130011.xlsx"),
    Path("input/all_markets_202307_202312_481292_20240607130013.xlsx"),
]
CURRENCY_CODE_FILE_PATH = Path("input/ISO4217_Currency_Code.xls")
VIX_FILE_PATH = Path("input/VIX_History.csv")
MIC_FILE_PATH = Path("input/ISO10383_MIC.xlsx")
CLEANED_DATASET_FILE_PATH = Path("output/cleaned_dataset.csv")

CLEANED_COLUMN_NAMES = [
    "Region",
    "Indicator Name",
    "ExchangeName",
    "CurrencyName",
    "Value",
    "Nominal",
    "DataType",
    "YTD",
    "% Change (YTD)",
    "% Change (MTM)",
    "MTM_pct",
    "% Change (YTY)",
    "YTY_pct",
    "AggregationType",
    "MIC",
    "OPERATING MIC",
    "currency_code",
    "OPEN",
    "HIGH",
    "LOW",
    "CLOSE",
    "Date",
]
MTM_PCT_COLUMN_NAME = "MTM_pct"
AVG_MTM_PCT_COLUMN_NAME = "AVG_MTM_pct"
YTY_PCT_COLUMN_NAME = "YTY_pct"
AVG_YTY_PCT_COLUMN_NAME = "AVG_YTY_pct"
MIC_COLUMN_NAME = "MIC"
OPERATING_MIC_COLUMN_NAME = "OPERATING MIC"
CURRENCY_NAME_COLUMN_NAME = "CurrencyName"
CURRENCY_COLUMN_NAME = "Currency"
ALPHABETIC_CODE_COLUMN_NAME = "Alphabetic Code"
MARKET_NAME_INSTITUTION_DESCRIPTION_COLUMN_NAME = "MARKET NAME-INSTITUTION DESCRIPTION"
CURRENCY_CODE_COLUMN_NAME = "currency_code"
EXCHANGE_NAME_COLUMN_NAME = "ExchangeName"
VIX_DATE_COLUMN_NAME = "DATE"
DATE_COLUMN_NAME = "Date"
YEAR_COLUMN_NAME = "Year"
MONTH_COLUMN_NAME = "Month"
OPEN_COLUMN_NAME = "OPEN"
HIGH_COLUMN_NAME = "HIGH"
LOW_COLUMN_NAME = "LOW"
CLOSE_COLUMN_NAME = "CLOSE"
VALUE_COLUMN_NAME = "Value"
ANNUAL_VALUE_COLUMN_NAME = "Annual Value"


# Constants for data quality checks
NEGATIVE_CHECK_COLUMN_NAMES = ["Value", "OPEN", "HIGH", "LOW", "CLOSE", "YTD"]
STRING_LENGTH_CHECK_COLUMN_NAMES = [
    "Region",
    "Indicator Name",
    "ExchangeName",
    "CurrencyName",
    "DataType",
    "AggregationType",
    "MIC",
    "OPERATING MIC",
    "currency_code",
    "MARKET NAME-INSTITUTION DESCRIPTION",
]
EXPECTED_DTYPE = {
    "Region": "object",
    "Indicator Name": "object",
    "ExchangeName": "object",
    "CurrencyName": "object",
    "DataType": "object",
    "AggregationType": "object",
    "MIC": "object",
    "OPERATING MIC": "object",
    "currency_code": "object",
    "Value": "float64",
    "Nominal": "int64",
    "OPEN": "float64",
    "HIGH": "float64",
    "LOW": "float64",
    "CLOSE": "float64",
    "YTD": "float64",
    "% Change (YTD)": "float64",
    "% Change (MTM)": "float64",
    "MARKET NAME-INSTITUTION DESCRIPTION": "object",
    "% Change (YTY)": "float64",
}
