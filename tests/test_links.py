from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from resolve_links import resolve
from archive_note import archive


class LinkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.note = self.root / "学习笔记.md"

    def test_no_vault_even_if_target_exists(self):
        (self.root / "微调.md").write_text("existing", encoding="utf-8")
        self.assertEqual(resolve(self.note, ["微调"])[0]["text"], "微调")

    def test_existing_unique_file_and_missing(self):
        (self.root / ".obsidian").mkdir()
        (self.root / "概念").mkdir()
        (self.root / "概念/微调.md").write_text("existing", encoding="utf-8")
        results = resolve(self.note, ["微调", "提示工程"])
        self.assertEqual(results[0]["text"], "[[概念/微调|微调]]")
        self.assertEqual(results[1]["status"], "plain_missing")
        self.assertFalse((self.root / "提示工程.md").exists())

    def test_ambiguous_files_and_disabled(self):
        (self.root / ".obsidian").mkdir()
        for folder in ("one", "two"):
            (self.root / folder).mkdir()
            (self.root / folder / "微调.md").write_text("existing", encoding="utf-8")
        self.assertEqual(resolve(self.note, ["微调"])[0]["status"], "plain_ambiguous")
        self.assertEqual(resolve(self.note, ["微调"], mode="off")[0]["text"], "微调")

    def test_existing_aggregate_heading(self):
        (self.root / ".obsidian").mkdir()
        archive(self.note, "微调", "body", "example")
        result = resolve(self.note, ["微调"])[0]
        self.assertEqual(result["status"], "linked")
        self.assertTrue(result["text"].startswith("[[学习笔记#1. 微调（"))
        self.assertTrue(result["text"].endswith("|微调]]"))

    def test_ignore_code_and_ambiguous_headings(self):
        (self.root / ".obsidian").mkdir()
        self.note.write_text("```md\n# 微调\n```\n", encoding="utf-8")
        self.assertEqual(resolve(self.note, ["微调"])[0]["status"], "plain_missing")
        self.note.write_text("## 微调\n## 微调\n", encoding="utf-8")
        self.assertEqual(resolve(self.note, ["微调"])[0]["status"], "plain_ambiguous")

    def test_vault_must_contain_note(self):
        other = self.root / "other"
        other.mkdir()
        (other / ".obsidian").mkdir()
        self.assertEqual(resolve(self.note, ["微调"], configured=other)[0]["status"], "plain_no_vault")

    def test_plain_title_without_dangling_link(self):
        archive(self.note, "RAG", "body", "one")
        self.assertNotIn("[[RAG]]", self.note.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
