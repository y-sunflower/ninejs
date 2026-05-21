from __future__ import annotations

from ninejs.typing import Pathish


def js_from_file(javascript_file: Pathish) -> str:
    with open(javascript_file, "r") as f:
        javascript: str = f.read()
    return javascript


class javascript:
    """
    Utility class to handle JavaScript injection for interactive plots.

    This class provides multiple ways to load JavaScript: directly from a
    string or from a JavaScript file. It is intended to be combined with
    `interactive()`.

    WARNING:
        JavaScript added through this class is executed directly in the
        generated HTML page. Only use code from sources you trust. Running
        untrusted JavaScript may expose sensitive data or execute malicious
        actions in the user's browser.

    Arguments:
        from_string: JavaScript code as a string.
        from_file: Path to a JavaScript file.

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
        from_string: str | None = None,
        *,
        from_file: Pathish | None = None,
    ) -> None:
        provided = [from_string is not None, from_file is not None]

        if sum(provided) != 1:
            raise ValueError(
                "Exactly one of 'from_string' or 'from_file' must be provided."
            )

        if from_string is not None:
            self.javascript_content: str = from_string
            return

        assert from_file is not None
        self.javascript_content = js_from_file(from_file)
