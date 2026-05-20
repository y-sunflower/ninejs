from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


APP_FILE = Path(__file__).with_name("app-streamlit.py")


@pytest.fixture()
def app():
    return AppTest.from_file(str(APP_FILE)).run()


def test_streamlit_app_runs_without_exceptions(app):
    assert not app.exception


def test_streamlit_app_renders_intro_markdown(app):
    assert len(app.markdown) == 1
    assert app.markdown[0].value == "# My first app\nHello *world!*"


def test_streamlit_app_renders_ninejs_iframe(app):
    iframe = app.get("iframe")

    assert len(iframe) == 1
    assert iframe[0].type == "iframe"
    assert 'title="ninejs interactive plot"' in iframe[0].proto.srcdoc
    assert "plot-container" in iframe[0].proto.srcdoc
    assert "plot-data" in iframe[0].proto.srcdoc
