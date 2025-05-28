MIC_COLUMN_NAME = "MIC"
CURRENCY_CODE_COLUMN_NAME = "currency_code"
EXCHANGE_NAME_COLUMN_NAME = "ExchangeName"
DATE_COLUMN_NAME = "Date"
VALUE_COLUMN_NAME = "Value"
NEGATIVE_CHECK_COLUMN_NAMES = ['Value', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'YTD']
STRING_LENGTH_CHECK_COLUMN_NAMES = ['Region', 'Indicator Name', 'ExchangeName', 'CurrencyName', 'DataType', 'AggregationType', 'MIC', 'OPERATING MIC', 'currency_code', 'MARKET NAME-INSTITUTION DESCRIPTION']
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
    "% Change (YTY)": "float64"
}