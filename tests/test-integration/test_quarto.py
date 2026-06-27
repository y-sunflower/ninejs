from pathlib import Path
import shutil
import subprocess

import pytest

from tests._ninejs_assertions import assert_ninejs_iframe


REPO_ROOT = Path(__file__).parents[2]
QUARTO_FILE = Path(__file__).with_name("quarto.qmd")


@pytest.mark.skipif(shutil.which("quarto") is None, reason="Quarto is not installed")
def test_quarto_document_embeds_ninejs_iframe(tmp_path):
    quarto_file = tmp_path / "quarto.qmd"
    shutil.copy2(QUARTO_FILE, quarto_file)

    subprocess.run(
        [
            "quarto",
            "render",
            str(quarto_file),
            "--output-dir",
            str(tmp_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    html = (tmp_path / "quarto.html").read_text(encoding="utf-8")
    assert_ninejs_iframe(html)
