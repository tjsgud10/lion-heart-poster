import io
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from streamlit.testing.v1 import AppTest

from collect_charts import collect
from poster import STYLES, demo_brief, render, validate_brief


class PosterTests(unittest.TestCase):
    def test_styles_and_korean_title(self):
        outputs = []
        for style in STYLES:
            png, mode = render("사자의 마음", "소녀시대", demo_brief(""), style)
            image = Image.open(io.BytesIO(png))
            self.assertEqual((image.format, image.size), ("PNG", (1024, 1536)))
            image.verify()
            self.assertEqual(mode, "엽서 데모")
            outputs.append(png)
        self.assertEqual(len(set(outputs)), len(STYLES))

    def test_copied_lyrics_and_invalid_palette(self):
        phrase = "A garden of ancient lights"
        brief = dict(summary=phrase, mood="Retro", imagery=["Roses"],
                     palette=["#112233", "#223344", "#334455"], blocked=False)
        with self.assertRaises(ValueError):
            validate_brief(brief, phrase)
        self.assertEqual(validate_brief(brief, "New material"), brief)
        with self.assertRaises(ValueError):
            validate_brief(dict(brief, palette=["invalid"] * 3), "")

    def test_demo_app_clears_lyrics_and_generates(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "streamlit_app.py")).run(timeout=20)
        self.assertFalse(app.exception)
        canary = "CANARY words never belong in the finished art brief"
        app.text_area[0].set_value(canary)
        app.button[0].click().run(timeout=20)
        self.assertFalse(app.exception)
        self.assertEqual(app.text_area[0].value, "")
        self.assertNotIn(canary, repr(app.session_state))
        app.button[1].click().run(timeout=20)
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["result"][2][:8], b"\x89PNG\r\n\x1a\n")
        self.assertTrue(app.get("download_button"))

    def test_chart_same_day_replaces_history(self):
        payload = {"tracks": {"track": [{"name": "Lion Heart",
                                         "artist": {"name": "Girls’ Generation"}}]}}
        def reply(*args, **kwargs):
            return io.StringIO(json.dumps(payload))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for _ in range(2):
                collect("test-key", root, reply, "2026-11-08")
            data = json.loads((root / "charts/global.json").read_text(encoding="utf-8"))
            self.assertEqual(data["tracks"][0]["title"], "Lion Heart")
            self.assertEqual(len((root / "history/global.csv").read_text(encoding="utf-8").splitlines()), 2)
