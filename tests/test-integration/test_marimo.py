from pathlib import Path
import shutil
import subprocess

import pytest

from tests._ninejs_assertions import assert_ninejs_iframe


REPO_ROOT = Path(__file__).parents[2]
MARIMO_FILE = Path(__file__).with_name("script-marimo.py")


@pytest.mark.skipif(shutil.which("marimo") is None, reason="marimo is not installed")
def test_marimo_export_embeds_ninejs_iframe(tmp_path):
    subprocess.run(
        ["marimo", "check", str(MARIMO_FILE)],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    output_file = tmp_path / "marimo.html"
    subprocess.run(
        ["marimo", "export", "html", str(MARIMO_FILE), "-o", str(output_file)],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    assert_ninejs_iframe(
        output_file.read_text(encoding="utf-8"),
        require_iframe_attrs=False,
    )
