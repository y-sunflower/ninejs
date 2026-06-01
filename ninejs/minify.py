import re


def _minify_style(match: re.Match[str]) -> str:
    """
    Minify all styling code (e.g., CSS).
    """
    css_content = re.sub(r"/\*.*?\*/", "", match.group(2), flags=re.DOTALL)
    css_content = re.sub(r"\s+", " ", css_content)
    css_content = re.sub(r"\s*([{}:;,])\s*", r"\1", css_content)
    return f"{match.group(1)}{css_content.strip()}{match.group(3)}"


def _minify_script(match: re.Match[str]) -> str:
    """
    Minify all scripting code (e.g., JavaScript).
    """
    lines: list[str] = []
    for line in match.group(2).splitlines():
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith("//"):
            continue
        lines.append(stripped_line)

    return f"{match.group(1)}{' '.join(lines)}{match.group(3)}"


def _minify_html(html: str, extra_line: bool) -> str:
    """
    Minify all HTML.
    """
    html = re.sub(
        r"(<style\b[^>]*>)(.*?)(</style>)", _minify_style, html, flags=re.DOTALL
    )
    html = re.sub(
        r"(<script\b[^>]*>)(.*?)(</script>)", _minify_script, html, flags=re.DOTALL
    )
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    html = re.sub(r"\s+", " ", html)
    html = re.sub(r">\s+<", "><", html)
    html = html.strip()
    html = html + "\n" if extra_line else html

    return html
