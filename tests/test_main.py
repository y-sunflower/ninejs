import pytest

import package_name
from package_name import add_digit


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (1, 1, 2),
        (10, 1, 11),
        (10, 10, 20),
        (15, 0, 15),
    ],
)
def test_sum_digit(a, b, expected):
    assert add_digit(a, b) == expected


def test_version():
    assert package_name.__version__ == "0.1.0"
