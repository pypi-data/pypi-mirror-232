# -*- coding: UTF-8 -*-
# vim: expandtab tabstop=4 shiftwidth=4

import argparse
import sys
from datetime import datetime, timezone

import tsenum


def main():
    parser = argparse.ArgumentParser(
        prog="tsenum",
        description="Count timestamps with different step sizes. A reference time is used to add/"
        "subtract an offset to enumerate the timestamps. To format the timestamp"
        "strftime formating style is used.",
        epilog=f"tsenum v{tsenum.__version__}, Copyright (C) 2019 {tsenum.__author__} <{tsenum.__email__}>. "
        f"Licensed under {tsenum.__license__}. See source distribution for detailed copyright notices.",
    )

    parser.add_argument(
        "-u",
        "--utc",
        help="Current time is in UTC",
        dest="utc",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "-o",
        "--offset",
        help="Offset to enumerate from (default 0)",
        dest="offset",
        type=int,
        default=0,
    )

    parser.add_argument(
        "-c",
        "--count",
        help="Count to enumerate",
        dest="count",
        type=int,
        required=True,
    )

    parser.add_argument(
        "-s",
        "--step",
        help="Step width",
        dest="step",
        choices=[
            tsenum.Step.DAY.value,
            tsenum.Step.HOUR.value,
            tsenum.Step.MINUTE.value,
            tsenum.Step.SECOND.value,
            tsenum.Step.WEEK.value,
            tsenum.Step.YEAR.value,
        ],
        type=str,
        required=True,
    )

    parser.add_argument(
        "-p",
        "--pattern",
        help="Date pattern to use (see Python's strftime in datetime)",
        dest="pattern",
        type=str,
        required=True,
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    if args.utc:
        now = datetime.now(tz=timezone.utc)
    else:
        now = datetime.now().astimezone()

    for i in tsenum.enumerate_times(now, args.offset, args.count, tsenum.Step(args.step), args.pattern):
        print(i)
