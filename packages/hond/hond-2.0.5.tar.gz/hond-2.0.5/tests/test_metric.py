# MIT License
#
# Copyright (c) 2021 Clivern
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pytest

from hond.metric import Metric


def test_metric():
    """Metric Tests"""

    metric = Metric(
        "customers.1234567.cpu",
        20.2,
        {"agent": "ebe94451-f111-42f5-9778-da7db3f0bcde"},
        "732a5add-c21e-4423-bded-7a97ff0c8be8"
    )

    assert metric.name == "customers.1234567.cpu"
    assert metric.value == 20.2
    assert metric.meta == {"agent": "ebe94451-f111-42f5-9778-da7db3f0bcde"}
    assert metric.id == "732a5add-c21e-4423-bded-7a97ff0c8be8"
    assert metric.timestamp > 0

    metric = Metric(
        "customers.1234568.memory",
        22.2,
        {},
        None,
        1662503511
    )

    assert metric.name == "customers.1234568.memory"
    assert metric.value == 22.2
    assert metric.meta == {}
    assert metric.id != ""
    assert metric.timestamp == 1662503511
