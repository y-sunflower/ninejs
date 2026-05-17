from typing import Optional


def js_from_file(javascript_file: str) -> str:
    with open(javascript_file, "r") as f:
        javascript: str = f.read()
    return javascript


class javascript:
    """
    Utility class to handle JavaScript injection for interactive plots.

    This class provides multiple ways to load JavasScript: directly from a
    string or from a JavaScript file. It is intended to be combined with
    `interactive` plots.

    Arguments:
        from_string (str): JavaScript in a string.
        from_file (str): Path to a JavaScript file.

    ```python
    (
        interactive(p)
        + javascript("console.log('hello world')")
        + javascript(from_file="script.js")
        + save("output.html")
    )
    ```
    """

    def __init__(
        self,
        from_string: Optional[str] = None,
        *,
        from_file: Optional[str] = None,
    ):
        provided = [from_string is not None, from_file is not None]

        if sum(provided) != 1:
            raise ValueError(
                "Exactly one of 'from_string' or 'from_file' must be provided."
            )

        if from_string is not None:
            self.javascript_content = from_string
            return

        assert from_file is not None
        self.javascript_content = js_from_file(from_file)
