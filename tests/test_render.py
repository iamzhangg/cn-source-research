import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("render_evidence", ROOT / "scripts/render_evidence.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class EvidenceTests(unittest.TestCase):
    def test_example_renders(self):
        data = json.loads((ROOT / "examples/evidence.json").read_text(encoding="utf-8"))
        self.assertIn("Grade / stance", MODULE.render(data))

    def test_bad_url_is_rejected(self):
        data = json.loads((ROOT / "examples/evidence.json").read_text(encoding="utf-8"))
        data["items"][0]["url"] = "search snippet"
        with self.assertRaisesRegex(ValueError, "HTTP"):
            MODULE.validate(data)


if __name__ == "__main__":
    unittest.main()
