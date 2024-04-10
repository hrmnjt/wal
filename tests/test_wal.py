import pytest
from datetime import date
from wal.wal import open_log  # Adjust the import path as needed


def test_valid_date_YYYYMMDD(capfd):
    open_log(20230410)
    out, _ = capfd.readouterr()
    assert "opening 20230410.md" in out


def test_valid_date_MMDD(capfd):
    current_year = date.today().year
    open_log(
        1201
    )  # Assuming the test runs in a year where December 1st is a valid date
    out, _ = capfd.readouterr()
    assert f"opening {current_year}1201.md" in out


def test_valid_date_DD(capfd):
    current_year = date.today().year
    current_month = date.today().month
    formatted_month = f"{current_month:02d}"  # Ensuring month is two digits
    open_log(10)  # Assuming the test runs in a month where the 10th is a valid date
    out, _ = capfd.readouterr()
    assert f"opening {current_year}{formatted_month}10.md" in out


def test_invalid_date_negative():
    with pytest.raises(ValueError):
        open_log(-20230410)


def test_invalid_date_format():
    with pytest.raises(ValueError):
        open_log(123456789)  # More digits than expected


def test_invalid_month_date():
    with pytest.raises(ValueError):
        open_log(20231301)  # 13th month, invalid
