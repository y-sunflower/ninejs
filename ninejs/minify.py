import re

_SCRIPT_BLOCK_PATTERN: re.Pattern[str] = re.compile(
    r"<script\b[^>]*>.*?</script>", re.DOTALL
)


def _minify_style(match: re.Match[str]) -> str:
    """
    Minify all styling code (e.g., CSS).
    """
    css_content = re.sub(r"/\*.*?\*/", "", match.group(2), flags=re.DOTALL)
    css_content = re.sub(r"\s+", " ", css_content)
    css_content = re.sub(r"\s*([{}:;,])\s*", r"\1", css_content)
    return f"{match.group(1)}{css_content.strip()}{match.group(3)}"


def _minify_markup(html: str) -> str:
    """
    Minify markup (HTML and inline CSS) outside `<script>` blocks.
    """
    html = re.sub(
        r"(<style\b[^>]*>)(.*?)(</style>)", _minify_style, html, flags=re.DOTALL
    )
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    html = re.sub(r"\s+", " ", html)
    html = re.sub(r">\s+<", "><", html)
    return html


def _minify_html(html: str, extra_line: bool) -> str:
    """
    Minify all HTML. `<script>` blocks are kept verbatim: rewriting
    JavaScript with regexes is unsafe (comments, semicolon insertion,
    template literals), so script content is never touched.
    """
    parts: list[str] = []
    last_end = 0
    for match in _SCRIPT_BLOCK_PATTERN.finditer(html):
        parts.append(_minify_markup(html[last_end : match.start()]))
        parts.append(match.group(0))
        last_end = match.end()
    parts.append(_minify_markup(html[last_end:]))

    html = "".join(parts).strip()
    html = html + "\n" if extra_line else html

    return html
