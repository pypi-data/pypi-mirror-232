<img src="icon.png" height="92px" />

## Data Expectations  
_Are your data meeting your expectations?_

----

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/joocer/data_expectations/blob/main/LICENSE)
[![Regression Suite](https://github.com/joocer/data_expectations/actions/workflows/regression_suite.yaml/badge.svg)](https://github.com/joocer/data_expectations/actions/workflows/regression_suite.yaml)
[![Static Analysis](https://github.com/joocer/data_expectations/actions/workflows/static_analysis.yml/badge.svg)](https://github.com/joocer/data_expectations/actions/workflows/static_analysis.yml)
[![codecov](https://codecov.io/gh/joocer/data_expectations/branch/main/graph/badge.svg?token=XA60LUVH0W)](https://codecov.io/gh/joocer/data_expectations)
 [![Downloads](https://static.pepy.tech/badge/data-expectations)](https://pepy.tech/project/data-expectations)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI Latest Release](https://img.shields.io/pypi/v/data-expectations.svg)](https://pypi.org/project/data-expectations/)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fjoocer%2Fdata_expectations.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Fjoocer%2Fdata_expectations?ref=badge_shield)

Data Expectations is a Python library which takes a delarative approach to asserting qualities of your datasets. Instead of tests like `is_sorted` to determine if a column is ordered, the expectation is `column_values_are_increasing`. Most of the time you don't need to know _how_ it got like that, you are only interested _what_ the data looks like now.

Expectations can be used alongside, or in place of a schema validator, however Expectations is intended to perform validation of the data in a dataset, not the structure of a table. Records should be a Python dictionary (or dictionary-like object) and can be processed one-by-one, or against an entire list of dictionaries.

[Data Expectations](https://github.com/joocer/data_expectations) was inspired by the great [Great Expectations](https://github.com/great-expectations/great_expectations) library, but we wanted something lighter and easier to quickly set up and run. Data Expectations can do less, but it does it with a fraction of the effort and has zero dependencies. 

## Use Cases

- Use Data Expectations was as a step in data processing pipelines, testing the data conforms to expectations before it is committed to the warehouse.
- Use Data Expectations to simplify validating user supplied values.

## Provided Expectations

- **expect_column_to_exist** (column)
- **expect_column_values_to_not_be_null** (column)
- **expect_column_values_to_be_of_type** (column, expected_type, ignore_nulls:true)
- **expect_column_values_to_be_in_type_list** (column, type_list, ignore_nulls:true)
- **expect_column_values_to_be_more_than** (column, threshold, ignore_nulls:true)
- **expect_column_values_to_be_less_than** (column, threshold, ignore_nulls:true)
- **expect_column_values_to_be_between** (column, maximum, minimum, ignore_nulls:true)
- **expect_column_values_to_be_increasing** (column, ignore_nulls:true)
- **expect_column_values_to_be_decreasing** (column, ignore_nulls:true)
- **expect_column_values_to_be_in_set** (column, symbols, ignore_nulls:true)
- **expect_column_values_to_match_regex** (column, regex, ignore_nulls:true)
- **expect_column_values_to_match_like** (column, like, ignore_nulls:true)
- **expect_column_values_length_to_be** (column, length, ignore_nulls:true)
- **expect_column_values_length_to_be_between**  (column, maximum, minimum, ignore_nulls:true)

## Install

~~~bash
pip install data_expectations
~~~

Data Expectations has no external dependencies, can be used ad hoc and in-the-moment without complex set up.

## Example Usage

Testing Python Dictionaries

~~~python
import data_expectations as de
from data_expectations import Expectation
from data_expectations import Behaviors

TEST_DATA = {"name": "charles", "age": 12}

set_of_expectations = [
    Expectation(Behaviors.EXPECT_COLUMN_TO_EXIST, column="name"),
    Expectation(Behaviors.EXPECT_COLUMN_TO_EXIST, column="age"),
    Expectation(Behaviors.EXPECT_COLUMN_VALUES_TO_BE_BETWEEN, column="age", config={"minimum": 0, "maximum": 120}),
]

expectations = de.Expectations(set_of_expectations)
try:
    de.evaluate_record(expectations, TEST_DATA)
except de.errors.ExpectationNotMetError:  # pragma: no cover
    print("Data Didn't Meet Expectations")
~~~

Testing individual Values:

~~~python
import data_expectations as de
from data_expectations import Expectation
from data_expectations import Behaviors

expectation = Expectation(Behaviors.EXPECT_COLUMN_VALUES_TO_BE_BETWEEN, column="age", config={"minimum": 0, "maximum": 120})

try:
    expectation.test_value(55)
except de.errors.ExpectationNotMetError:  # pragma: no cover
    print("Data Didn't Meet Expectations")
~~~