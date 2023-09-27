from datetime import datetime

import pytest

from tsenum import Step, enumerate_times

TEST_DATETIME = datetime(year=1970, month=1, day=10, hour=1, minute=20, second=33).astimezone()

# test formating


def test_formating():
    r = enumerate_times(TEST_DATETIME, 0, 1, Step.DAY, "%Y")
    assert len(r) == 1
    assert "1970" in r

    r = enumerate_times(TEST_DATETIME, 0, 1, Step.DAY, "%m")
    assert len(r) == 1
    assert "01" in r

    r = enumerate_times(TEST_DATETIME, 0, 1, Step.DAY, "%d")
    assert len(r) == 1
    assert "10" in r


# test step size


def test_3weeks():
    r = enumerate_times(TEST_DATETIME, 0, 3, Step.WEEK, "%Y-%m-%d %H:%M:%S")
    assert len(r) == 3
    assert "1970-01-10 01:20:33" in r
    assert "1970-01-17 01:20:33" in r
    assert "1970-01-24 01:20:33" in r


def test_3days():
    r = enumerate_times(TEST_DATETIME, 0, 3, Step.DAY, "%Y-%m-%d %H:%M:%S")
    assert len(r) == 3
    assert "1970-01-10 01:20:33" in r
    assert "1970-01-11 01:20:33" in r
    assert "1970-01-12 01:20:33" in r


def test_3minutes():
    r = enumerate_times(TEST_DATETIME, 0, 3, Step.MINUTE, "%Y-%m-%d %H:%M:%S")
    assert len(r) == 3
    assert "1970-01-10 01:20:33" in r
    assert "1970-01-10 01:21:33" in r
    assert "1970-01-10 01:22:33" in r


def test_3seconds():
    r = enumerate_times(TEST_DATETIME, 0, 3, Step.SECOND, "%Y-%m-%d %H:%M:%S")
    assert len(r) == 3
    assert "1970-01-10 01:20:33" in r
    assert "1970-01-10 01:20:34" in r
    assert "1970-01-10 01:20:35" in r


def test_invalid_stepsize():
    with pytest.raises(ValueError):
        enumerate_times(TEST_DATETIME, 0, 3, "invalid", "%Y-%m-%d %H:%M:%S")


# test offset


def test_3seconds_minus_one():
    r = enumerate_times(TEST_DATETIME, -1, 3, Step.SECOND, "%Y-%m-%d %H:%M:%S")
    assert len(r) == 3
    assert "1970-01-10 01:20:32" in r
    assert "1970-01-10 01:20:33" in r
    assert "1970-01-10 01:20:34" in r


def test_3seconds_plus_three():
    r = enumerate_times(TEST_DATETIME, 3, 3, Step.SECOND, "%Y-%m-%d %H:%M:%S")
    assert len(r) == 3
    assert "1970-01-10 01:20:36" in r
    assert "1970-01-10 01:20:37" in r
    assert "1970-01-10 01:20:38" in r


# test range


def test_plus_3seconds():
    r = enumerate_times(TEST_DATETIME, 0, 3, Step.SECOND, "%Y-%m-%d %H:%M:%S")
    assert len(r) == 3
    assert "1970-01-10 01:20:33" in r
    assert "1970-01-10 01:20:34" in r
    assert "1970-01-10 01:20:35" in r


def test_minus_3seconds():
    r = enumerate_times(TEST_DATETIME, 0, -3, Step.SECOND, "%Y-%m-%d %H:%M:%S")
    assert len(r) == 3
    assert "1970-01-10 01:20:30" in r
    assert "1970-01-10 01:20:31" in r
    assert "1970-01-10 01:20:32" in r
