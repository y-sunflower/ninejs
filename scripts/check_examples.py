"""Sanity checks for docs/examples/.

Run from the repository root:

    uv run python scripts/check_examples.py

Static checks (always):
- only expected file types live in docs/examples/
- no file is unexpectedly large
- every script imports ninejs and calls save() with a literal
  "docs/iframes/<slug>.html" path
- no two scripts write the same iframe
- no absolute local paths (e.g. /Users/..., C:\\...)
- every support file (.css/.js/.csv) is referenced by at least one script
"""

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

ALLOWED_EXTENSIONS = {".py", ".csv", ".css", ".js"}
MAX_FILE_SIZE_MB = 10
SCRIPT_TIMEOUT_SECONDS = 300

SAVE_PATTERN = re.compile(r"""save\(\s*(?:f?["']([^"']*)["'])?""")
IFRAME_PATH_PATTERN = re.compile(r"^docs/iframes/[A-Za-z0-9._-]+\.html$")
ABSOLUTE_PATH_PATTERN = re.compile(r"""["'](?:/Users/|/home/|[A-Za-z]:\\)""")

errors: list[str] = []


def tracked_files() -> list[Path]:
    output = subprocess.run(
        ["git", "ls-files", "docs/examples"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [REPO_ROOT / line for line in sorted(output.splitlines())]


def check_static() -> dict[Path, list[str]]:
    """Run all static checks. Returns {script: [declared iframe paths]}."""
    save_targets: dict[Path, list[str]] = {}
    all_sources = ""
    files = tracked_files()

    for file in files:
        rel = file.relative_to(REPO_ROOT)

        if file.suffix not in ALLOWED_EXTENSIONS:
            errors.append(
                f"{rel}: unexpected file type '{file.suffix}'. Allowed: "
                f"{sorted(ALLOWED_EXTENSIONS)}. If intentional, update "
                "ALLOWED_EXTENSIONS in scripts/check_examples.py."
            )
            continue

        size_mb = file.stat().st_size / 1024**2
        if size_mb > MAX_FILE_SIZE_MB:
            errors.append(
                f"{rel}: file is {size_mb:.1f} MB (max {MAX_FILE_SIZE_MB} MB). "
                "Use a smaller dataset or load it from a URL."
            )

        if file.suffix != ".py":
            continue

        source = file.read_text()
        all_sources += source

        if "ninejs" not in source:
            errors.append(f"{rel}: does not import ninejs.")

        if ABSOLUTE_PATH_PATTERN.search(source):
            errors.append(
                f"{rel}: contains an absolute local path. Use paths relative "
                "to the repository root."
            )

        targets = []
        for match in SAVE_PATTERN.finditer(source):
            path = match.group(1)
            if path is None or "{" in path:
                errors.append(
                    f"{rel}: save() must be called with a literal path so CI "
                    "can verify the output."
                )
            elif not IFRAME_PATH_PATTERN.match(path):
                errors.append(
                    f"{rel}: save() writes to '{path}' but examples must save "
                    "to 'docs/iframes/<slug>.html'."
                )
            else:
                targets.append(path)

        if not source_has_save(source):
            errors.append(f"{rel}: never calls save(), so it produces no iframe.")
        save_targets[file] = targets

    # No two scripts should write the same iframe.
    seen: dict[str, Path] = {}
    for script, targets in save_targets.items():
        for target in targets:
            if target in seen and seen[target] != script:
                errors.append(
                    f"{script.relative_to(REPO_ROOT)} and "
                    f"{seen[target].relative_to(REPO_ROOT)} both write to "
                    f"'{target}'."
                )
            seen[target] = script

    # Support files must be referenced by at least one script.
    for file in files:
        if file.suffix in {".css", ".js", ".csv"} and file.name not in all_sources:
            errors.append(
                f"{file.relative_to(REPO_ROOT)}: not referenced by any example "
                "script. Remove it or reference it."
            )

    return save_targets


def source_has_save(source: str) -> bool:
    return re.search(r"\bsave\(", source) is not None


def main() -> int:
    save_targets = check_static()

    if errors:
        print(f"\n{len(errors)} problem(s) found in docs/examples/:\n")
        for error in errors:
            print(f"- {error}\n")
        return 1

    print(f"All checks passed for {len(save_targets)} example scripts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
