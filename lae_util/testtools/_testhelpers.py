# Copyright 2014-2016 ClusterHQ
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Helpers for testing our test code.

Only put stuff here that is specific to testing code about unit testing.

Originally ``flocker/testtools/_testhelpers.py``.
"""

from hypothesis.strategies import sampled_from
import unittest

from testtools.matchers import (
    AfterPreprocessing,
    Equals,
    MatchesStructure,
)

from ._base import TestCase


base_test_cases = sampled_from([TestCase])


def throw(exception):
    """
    Raise 'exception'.
    """
    raise exception


def only_skips(tests_run, reasons):
    """
    Matches results that only had skips, and only for the given reasons.
    """
    return has_results(
        tests_run=Equals(tests_run),
        skipped=AfterPreprocessing(
            lambda xs: list(unicode(x[1]) for x in xs),
            Equals(reasons)),
    )


def has_results(errors=None, failures=None, skipped=None,
                expected_failures=None, unexpected_successes=None,
                tests_run=None):
    """
    Return a matcher on test results.

    By default, will match a result that has no tests run.
    """
    if errors is None:
        errors = Equals([])
    if failures is None:
        failures = Equals([])
    if skipped is None:
        skipped = Equals([])
    if expected_failures is None:
        expected_failures = Equals([])
    if unexpected_successes is None:
        unexpected_successes = Equals([])
    if tests_run is None:
        tests_run = Equals(0)
    return MatchesStructure(
        errors=errors,
        failures=failures,
        skipped=skipped,
        expectedFailures=expected_failures,
        unexpectedSuccesses=unexpected_successes,
        testsRun=tests_run,
    )


def run_test(case):
    """
    Run a test and return its results.
    """
    # XXX: How many times have I written something like this?
    result = unittest.TestResult()
    case.run(result)
    return result


def make_test_case(base_case):
    """
    Make a single test that subclasses ``base_case`` and passes.

    :param type base_case: A ``TestCase`` class.

    :rtype: ``base_case``
    """
    class FooTests(base_case):
        def test_something(self):
            pass
    return FooTests('test_something')
