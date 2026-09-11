"""Shared configuration helpers. Python standard library only."""
import json
from pathlib import Path


def read_config(filename):
    path = Path(filename).expanduser().resolve()
    config = json.loads(path.read_text(encoding="utf-8-sig"))
    if config.get("archive_mode") not in ("explicit", "auto"):
        raise ValueError("archive_mode must be explicit or auto")
    if config.get("destination_kind", "unconfigured") not in ("unconfigured", "test", "notes", "obsidian"):
        raise ValueError("destination_kind must be unconfigured, test, notes or obsidian")
    for key in ("note_path", "image_dir"):
        value = config.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Missing configuration: {key}")
        target = Path(value).expanduser()
        config[key] = target if target.is_absolute() else path.parent / target
    browser = config.get("browser_path", "")
    vault = config.get("vault_path", "")
    if vault:
        target = Path(vault).expanduser()
        config["vault_path"] = target if target.is_absolute() else path.parent / target
    if config.get("wikilinks", "auto") not in ("auto", "off"):
        raise ValueError("wikilinks must be auto or off")
    if browser:
        target = Path(browser).expanduser()
        config["browser_path"] = str(target if target.is_absolute() else path.parent / target)
    return config


def validate_destination(config, require_obsidian=False):
    kind = config.get("destination_kind", "unconfigured")
    if kind == "unconfigured":
        raise ValueError("Destination not configured; select the user's real notes or an explicit test destination first")
    if require_obsidian and kind != "obsidian":
        raise ValueError("Obsidian was requested, but this configuration is not a confirmed Obsidian destination")
    if kind == "obsidian":
        root = config.get("vault_path")
        if not root:
            raise ValueError("An explicit vault_path is required for an Obsidian destination")
        root = Path(root).resolve()
        note = Path(config["note_path"]).resolve()
        if not (root / ".obsidian").is_dir() or not note.is_relative_to(root):
            raise ValueError("Note must be inside the configured Obsidian vault")
