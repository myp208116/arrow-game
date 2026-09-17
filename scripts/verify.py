"""Run real tests and save their output and environment for the report."""
import contextlib
import io
import json
import os
import platform
import sys
import unittest
from datetime import datetime
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

stream = io.StringIO()
with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
report = {
    "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
    "python": platform.python_version(), "platform": platform.system(),
    "pygame-ce": version("pygame-ce"), "tests_run": result.testsRun,
    "failures": len(result.failures), "errors": len(result.errors),
    "passed": result.wasSuccessful(),
    "method": "unittest + real Pygame mouse-event handlers; SDL dummy display",
    "human_playtest": "not yet recorded",
}
(ROOT / "docs/test-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
(ROOT / "docs/test-output.txt").write_text(stream.getvalue(), encoding="utf-8")
print(stream.getvalue())
print(json.dumps(report, indent=2))
raise SystemExit(0 if result.wasSuccessful() else 1)
