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

    Arguments:
        minify: Whether to minify HTML output. If `True`, whitespace is
            collapsed outside `<script>` blocks; script content is kept
            verbatim. The main use case for this is to avoid tracking
            large generated files.
        extra_line: Whether to add an extra blank line when `minify` is
            `True`. This is mostly useful for you track your exported HTML
            file and use hooks that check for an extra blank line.

    ```python
    html_plot: str = interactive(p) + to_html()
    html_plot: str = interactive(p) + to_html(minify=True)
    ```
    """

    def __init__(self, *, minify: bool = False, extra_line: bool = True) -> None:
        self.minify: bool = minify
        self.extra_line: bool = extra_line


class to_iframe:
    """
    Utility class to export an interactive plot as an iframe HTML string.

    Arguments:
        width: Width of the iframe. If an integer, it is converted to pixels.
        height: Height of the iframe. If an integer, it is converted to pixels.
        title: Title of the iframe.
        sandbox: Attribute to allow specific behaviors, such as running JavaScript.
            Learn more: https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe

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
    ) -> None:
        self.width: int | str = width
        self.height: int | str = height
        self.title: str = title
        self.sandbox: str | None = sandbox
        self.style: str = (
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
