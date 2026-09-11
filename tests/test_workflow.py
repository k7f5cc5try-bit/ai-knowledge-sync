import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from archive_note import archive, ANCHOR
from common import read_config
from svg2png import validate_svg, check_png, convert


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.note = self.root / "notes.md"

    def test_create_and_retry(self):
        self.assertEqual(archive(self.note, "RAG", "body", "one")["status"], "created")
        before = self.note.read_bytes()
        self.assertEqual(archive(self.note, "RAG", "body", "one")["status"], "already_exists")
        self.assertEqual(archive(self.note, "RAG", "body", "two")["status"], "already_exists")
        self.assertEqual(before, self.note.read_bytes())
        with self.assertRaises(ValueError):
            archive(self.note, "RAG", "changed", "one")

    def test_preserves_history_and_numbering(self):
        before = ("# 笔记\r\n### 8. 原记录\r\n保持原样\r\n\r\n" + ANCHOR + "\r\n历史纠正\r\n").encode("utf-8")
        self.note.write_bytes(before)
        self.assertEqual(archive(self.note, "Agent", "new", "next")["number"], 9)
        after = self.note.read_bytes()
        prefix, suffix = before.split(ANCHOR.encode())
        self.assertTrue(after.startswith(prefix))
        self.assertTrue(after.endswith(ANCHOR.encode() + suffix))

    def test_invalid_anchors_do_not_write(self):
        for text in ("existing note", ANCHOR + "\n" + ANCHOR):
            self.note.write_text(text, encoding="utf-8")
            before = self.note.read_bytes()
            with self.assertRaises(ValueError):
                archive(self.note, "RAG", "body", "one")
            self.assertEqual(before, self.note.read_bytes())

    def test_lock_blocks_writer(self):
        self.note.with_name("notes.md.lock").touch()
        with self.assertRaises(FileExistsError):
            archive(self.note, "RAG", "body", "one")
        self.assertFalse(self.note.exists())

    def test_relative_config(self):
        config = self.root / "config.json"
        config.write_text(json.dumps({"archive_mode": "explicit", "note_path": "笔记/a.md", "image_dir": "images"}), encoding="utf-8")
        self.assertEqual(read_config(config)["note_path"], self.root / "笔记/a.md")

    def test_rejects_external_svg_and_variables(self):
        source = self.root / "a.svg"
        for body in ('<image href="https://example.com/a.png"/>', '<script/>', '<rect fill="var(--color)"/>'):
            source.write_text('<svg xmlns="http://www.w3.org/2000/svg">' + body + '</svg>', encoding="utf-8")
            with self.assertRaises(ValueError):
                validate_svg(source)

    def test_failed_conversion_does_not_publish_stale_image(self):
        source = Path(__file__).resolve().parents[1] / "examples/diagram.svg"
        destination = self.root / "images"
        destination.mkdir()
        old = destination / "old.png"
        old.write_bytes(b"old image")
        with patch("svg2png.subprocess.run") as run:
            run.return_value.returncode = 1
            with self.assertRaises(RuntimeError):
                convert(source, destination, "RAG", 680, 290, 2, "browser")
        self.assertEqual(list(destination.iterdir()), [old])
        self.assertEqual(old.read_bytes(), b"old image")

    def test_invalid_png_rejected(self):
        output = self.root / "fake.png"
        output.write_bytes(b"not png")
        with self.assertRaises(ValueError):
            check_png(output, (680, 290))


if __name__ == "__main__":
    unittest.main()
