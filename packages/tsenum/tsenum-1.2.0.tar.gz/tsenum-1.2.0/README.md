# tsenum

[![Tests](https://github.com/aboehm/tsenum/actions/workflows/tests.yml/badge.svg)](https://github.com/aboehm/tsenum/actions/workflows/tests.yml)

A timestamp generator.

## Install

You can use pip to install from the repository

```
pip install tsenum
```

or download sources and run pip from this directory

```
git clone https://github.com/aboehm/tsenum
pip install .
```

## Usage

`tsenum` provides an CLI. For help run:

```
tsenum -h
```

To count 7 days back from yesterday via CLI, run:

```sh
tsenum --offset -1 --count -7 --step day --pattern "%Y-%m-%d: Hello world!"
2016-05-27: Hello world!
2016-05-28: Hello world!
2016-05-29: Hello world!
2016-05-30: Hello world!
2016-05-31: Hello world!
2016-06-01: Hello world!
2016-06-02: Hello world!
```

To do it programmatically:

```python
from datetime import datetime
import tsenum

print(
    tsenum.enumerate_times(
        datetime.now().astimezone(),
        offset=-1,
        count=-7,
        step=tsenum.Step.DAY,
        pattern='%Y-%m-%d'
    )
)
```
