"""Read-only, conservative Obsidian link resolution for existing concept names."""
import argparse
import json
from pathlib import Path
import re
from common import read_config


def vault_for(note, configured=None, mode="auto"):
    if mode == "off":
        return None
    note = Path(note).resolve()
    roots = [Path(configured).resolve()] if configured else list(note.parents)
    for root in roots:
        if (root / ".obsidian").is_dir() and note.is_relative_to(root):
            return root
    return None


def headings(text):
    fence = None
    frontmatter = False
    for index, line in enumerate(text.splitlines()):
        if index == 0 and line == "---":
            frontmatter = True
            continue
        if frontmatter:
            if line in ("---", "..."):
                frontmatter = False
            continue
        mark = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if mark:
            if fence is None:
                fence = mark[1]
            elif mark[1][0] == fence[0] and len(mark[1]) >= len(fence):
                fence = None
            continue
        if fence:
            continue
        match = re.match(r"^#{1,6} +(.+?)\s*#*\s*$", line)
        if match:
            heading = match[1]
            concept = re.sub(r"^\d+\.\s+", "", heading)
            concept = re.sub(r"（\d{4}-\d{2}-\d{2} 新增）$", "", concept).strip()
            yield concept, heading


def resolve(note, names, configured=None, mode="auto"):
    if mode not in ("auto", "off"):
        raise ValueError("wikilinks must be auto or off")
    for name in names:
        if not name.strip() or any(c in name for c in "[]|#\r\n<>"):
            raise ValueError("Concepts must be plain names, without link syntax")
    vault = vault_for(note, configured, mode)
    output = [{"name": name, "text": name, "status": "plain_no_vault"} for name in names]
    if vault is None:
        return output
    files = []
    for path in vault.rglob("*.md"):
        if any(part.startswith(".") for part in path.relative_to(vault).parts):
            continue
        if not path.resolve().is_relative_to(vault) or path.is_symlink():
            continue
        relative = path.relative_to(vault).with_suffix("").as_posix()
        if any(c in relative for c in "[]|#\r\n"):
            continue
        try:
            content = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError):
            continue
        files.append((path.stem, relative, list(headings(content))))
    for item in output:
        name = item["name"]
        pages = [relative for stem, relative, _ in files if stem == name]
        targets = pages
        if not targets:
            targets = [relative + "#" + heading for _, relative, entries in files
                       for concept, heading in entries if concept == name
                       and not any(c in heading for c in "[]|#\r\n")]
        if len(targets) == 1:
            item.update(text=f"[[{targets[0]}|{name}]]", status="linked")
        else:
            item["status"] = "plain_ambiguous" if targets else "plain_missing"
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--names", nargs="+", required=True)
    args = parser.parse_args()
    try:
        config = read_config(args.config)
        result = resolve(config["note_path"], args.names, config.get("vault_path"), config.get("wikilinks", "auto"))
        print(json.dumps(result, ensure_ascii=False))
    except (OSError, ValueError) as error:
        parser.exit(1, f"Link check failed: {error}\n")


if __name__ == "__main__":
    main()
