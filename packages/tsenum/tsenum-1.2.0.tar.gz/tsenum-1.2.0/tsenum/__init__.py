# -*- coding: UTF-8 -*-
# vim: expandtab tabstop=4 shiftwidth=4

__version__ = "1.2.0"
__author__ = "Alexander Böhm"
__email__ = "alexander.boehm@malbolge.net"
__license__ = "GPLv2+"

from datetime import datetime, timedelta
from enum import Enum
from typing import List


class Step(Enum):
    DAY = "day"
    HOUR = "hour"
    MINUTE = "minute"
    SECOND = "second"
    WEEK = "week"
    YEAR = "year"


def enumerate_times(cur_time: datetime, offset: int, count: int, step: Step, pattern: str) -> List[str]:
    """
    Count a number of timestamps from a specific time at a given offset. Timestamps
    are formated with strftime.

    Parameters:
        cur_time (datetime): Reference time

        offset (int): Offset added/subtracted in given unit from refrence time

        count (int): Timestamps to count in given unit. Positive and negative integers are possible.

        step (Step): Step size counting in.

        pattern (str): Timestamp pattern in strftime format

    Returns:
        A list of strings of the pattern.
    """

    if step == Step.DAY:

        def step_func(step, offset):
            return timedelta(days=(step + offset))

    elif step == Step.HOUR:

        def step_func(step, offset):
            return timedelta(hours=(step + offset))

    elif step == Step.MINUTE:

        def step_func(step, offset):
            return timedelta(minutes=(step + offset))

    elif step == Step.SECOND:

        def step_func(step, offset):
            return timedelta(seconds=(step + offset))

    elif step == Step.WEEK:

        def step_func(step, offset):
            return timedelta(weeks=(step + offset))

    elif step == Step.YEAR:

        def step_func(step, offset):
            return timedelta(years=(step + offset))

    else:
        msg = f"Stepsize `{step}` is not defined"
        raise ValueError(msg)

    l_count = (count < 0) * count
    h_count = (count >= 0) * count
    return [(cur_time + step_func(i, offset)).strftime(pattern) for i in range(l_count, h_count)]
