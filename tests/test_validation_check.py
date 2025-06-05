import pytest
import pandas as pd
import sys

sys.path.append("src") 

from src.quality_checks import ValidationCheck  
from constants import MIC_COLUMN_NAME, CURRENCY_CODE_COLUMN_NAME


@pytest.fixture
def valid_data():
    return pd.DataFrame({
        MIC_COLUMN_NAME: ["XNAS", "XLON", "BATS"],
        CURRENCY_CODE_COLUMN_NAME: ["USD", "EUR", "JPY"]
    })


@pytest.fixture
def invalid_mic_data():
    return pd.DataFrame({
        MIC_COLUMN_NAME: ["XN", "12345", "!!$$", None],
        CURRENCY_CODE_COLUMN_NAME: ["USD", "EUR", "JPY", "GBP"]
    })


@pytest.fixture
def invalid_currency_code_data():
    return pd.DataFrame({
        MIC_COLUMN_NAME: ["XNAS", "XLON", "BATS", "XTKS"],
        CURRENCY_CODE_COLUMN_NAME: ["usd", "Eur", "123", None]
    })


def test_valid_data(valid_data):
    checker = ValidationCheck(valid_data)
    result = checker.run_check()
    assert result == {}


def test_invalid_mic_data(invalid_mic_data):
    checker = ValidationCheck(invalid_mic_data)
    result = checker.run_check()
    assert "mic_format_check" in result
    assert MIC_COLUMN_NAME in result["mic_format_check"]
    assert len(result["mic_format_check"][MIC_COLUMN_NAME]) == 4


def test_invalid_currency_code_data(invalid_currency_code_data):
    checker = ValidationCheck(invalid_currency_code_data)
    result = checker.run_check()
    assert "currency_code_format_check" in result
    assert CURRENCY_CODE_COLUMN_NAME in result["currency_code_format_check"]
    assert len(result["currency_code_format_check"][CURRENCY_CODE_COLUMN_NAME]) == 4


def test_missing_mic_column():
    df = pd.DataFrame({
        CURRENCY_CODE_COLUMN_NAME: ["USD", "EUR", "JPY"]
    })
    checker = ValidationCheck(df)
    with pytest.raises(ValueError, match=f"Column '{MIC_COLUMN_NAME}' not found"):
        checker.run_check()


def test_missing_currency_column():
    df = pd.DataFrame({
        MIC_COLUMN_NAME: ["XNAS", "XLON", "BATS"]
    })
    checker = ValidationCheck(df)
    with pytest.raises(ValueError, match=f"Column '{CURRENCY_CODE_COLUMN_NAME}' not found"):
        checker.run_check()