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

    Attributes:
        javascript_content (str): The JavaScript rules to be injected.

    Example:
        ```python
        (
            interactive(p)
            + javascript("console.log('hello world')")
            + save("output.html")
        )
        ```
    """

    def __init__(self, from_string=None, *, from_file=None):
        if from_string is not None:
            self.javascript_content = from_string
        elif from_file is not None:
            self.javascript_content = js_from_file(from_file)
