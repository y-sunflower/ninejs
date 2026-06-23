from ninejs.main import MAIN_DIR
from ninejs.javascript import js_from_file


def confetti(
    particle_count: int = 100,
    spread: int = 70,
    origin: dict = dict(y=0.6),
) -> str:
    """
    Return JavaScript that triggers a confetti burst.

    Args:
        particle_count: Number of confetti particles to emit.
        spread: Angle, in degrees, over which particles are spread.
        origin: Confetti origin passed to the browser-side confetti function.

    Returns:
        JavaScript code that loads the bundled confetti effect if needed and runs it.
    """
    script = f"""
    globalThis.confetti({{
        particleCount: {particle_count},
        spread: {spread},
        origin: {str(origin).replace("'", "")},
    }});
    """
    confetti_path = MAIN_DIR / "effects" / "confettieffect" / "confetti.min.js"
    confetti_script = f"""
    if (typeof globalThis.confetti !== "function") {{
        {js_from_file(confetti_path)}
    }}
    {script}
    """
    return confetti_script
