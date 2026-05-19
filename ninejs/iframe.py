from html import escape


def _css_size(value: int | str) -> str:
    if isinstance(value, int):
        return f"{value}px"

    return value


def _html_attr(name: str, value: object | None) -> str:
    if value is None:
        return ""

    return f' {name}="{escape(str(value), quote=True)}"'


class to_html:
    """
    Utility class to export an interactive plot as an HTML string.

    ```python
    html_plot: str = interactive(p) + to_html()
    ```
    """

    def __init__(self) -> None:
        pass


class to_iframe:
    """
    Utility class to export an interactive plot as an iframe HTML string.

    ```python
    iframe_plot: str = interactive(p) + to_iframe(height=650)
    ```
    """

    def __init__(
        self,
        *,
        width: int | str = "100%",
        height: int | str = 600,
        title: str = "ninejs interactive plot",
        sandbox: str | None = "allow-scripts",
        style: str | None = None,
    ) -> None:
        self.width: int | str = width
        self.height: int | str = height
        self.title: str = title
        self.sandbox: str | None = sandbox
        self.style: str = style or (
            f"width:{_css_size(width)};height:{_css_size(height)};border:0;"
        )

    def render(self, html_content: str) -> str:
        return (
            "<iframe"
            f"{_html_attr('srcdoc', html_content)}"
            f"{_html_attr('title', self.title)}"
            f"{_html_attr('style', self.style)}"
            f"{_html_attr('sandbox', self.sandbox)}"
            "></iframe>"
        )
