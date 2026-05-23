from ninejs.main import MAIN_DIR
from ninejs.javascript import js_from_file

confetti_path = MAIN_DIR / "effects" / "confettieffect"
confetti = f"""
if (typeof globalThis.confetti !== "function") {{
{js_from_file(confetti_path / "confetti.min.js")}
}}
{js_from_file(confetti_path / "confetti.js")}
"""
