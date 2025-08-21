import narwhals.stable.v2 as nw
from narwhals.stable.v2.dependencies import is_numpy_array, is_into_series

import re


def _vector_to_list(vector, name="labels and groups") -> list:
    """
    Function used to easily convert various kind of iterables to
    lists in order to have standardised objects passed to javascript.

    It accepts all backend series from narwhals and common objects
    such as numpy arrays.

    Todo: test this extensively to make sure it behaves as expected.

    Args:
        vector: A valid iterable.
        name: The name passed to the error message when type is
            invalid.

    Returns:
        A list
    """
    if isinstance(vector, (list, tuple)) or is_numpy_array(vector):
        return list(vector)
    elif is_into_series(vector):
        return nw.from_native(vector, allow_series=True).to_list()
    else:
        raise ValueError(
            f"{name} must be a Series or a valid iterable (list, tuple, ndarray...)."
        )


def _get_and_sanitize_js(file_path, after_pattern):
    with open(file_path) as f:
        content = f.read()

    match = re.search(after_pattern, content, re.DOTALL)
    if match:
        return match.group(0)
    else:
        raise ValueError(f"Could not find '{after_pattern}' in the file")
