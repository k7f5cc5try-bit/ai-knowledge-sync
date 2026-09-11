from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from common import validate_destination


class DestinationTests(unittest.TestCase):
    def test_unconfigured_blocks(self):
        with self.assertRaises(ValueError):
            validate_destination({})

    def test_test_cannot_satisfy_obsidian(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / '.obsidian').mkdir()
            config = {'destination_kind': 'test', 'vault_path': root, 'note_path': root / 'note.md'}
            validate_destination(config)
            with self.assertRaises(ValueError):
                validate_destination(config, require_obsidian=True)

    def test_generic_notes_cannot_satisfy_obsidian(self):
        with self.assertRaises(ValueError):
            validate_destination({'destination_kind': 'notes'}, require_obsidian=True)

    def test_obsidian_requires_containment(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / '.obsidian').mkdir()
            config = {'destination_kind': 'obsidian', 'vault_path': root, 'note_path': root / 'notes/note.md'}
            validate_destination(config, require_obsidian=True)
            config['note_path'] = root.parent / 'outside.md'
            with self.assertRaises(ValueError):
                validate_destination(config, require_obsidian=True)

    def test_obsidian_requires_vault(self):
        with self.assertRaises(ValueError):
            validate_destination({'destination_kind': 'obsidian'}, require_obsidian=True)
