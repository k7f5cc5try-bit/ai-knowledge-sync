"""Insert an idempotent entry without changing existing note bytes."""
import argparse
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from common import read_config, validate_destination

ANCHOR = "## 关键纠正清单（易错点）"


def archive(note, title, body, entry_id):
    note = Path(note)
    if not title.strip() or any(c in title for c in "\r\n[]<>"):
        raise ValueError("Title must be a nonempty single line without brackets or angle brackets")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", entry_id):
        raise ValueError("entry-id must contain 1-100 letters, digits, underscores or hyphens")
    body = body.strip()
    if not body or "<!-- ai-sync:" in body or ANCHOR in body:
        raise ValueError("Body is empty or contains a reserved marker")
    digest = hashlib.sha256((title + "\n" + body).encode("utf-8")).hexdigest()
    marker = f"<!-- ai-sync:{entry_id}:{digest} -->"
    note.parent.mkdir(parents=True, exist_ok=True)
    lock = note.with_name(note.name + ".lock")
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(fd)
    temporary = None
    try:
        existed = note.exists()
        original = note.read_bytes() if existed else b""
        baseline = original if existed else ("# AI 学习笔记\n\n" + ANCHOR + "\n").encode("utf-8")
        text = baseline.decode("utf-8")
        matches = list(re.finditer(r"(?m)^" + re.escape(ANCHOR) + r"\r?$", text))
        if len(matches) != 1:
            raise ValueError("Existing note must contain exactly one anchor; no changes made")
        entries = re.findall(r"<!-- ai-sync:([A-Za-z0-9_-]+):([a-f0-9]{64}) -->", text)
        for saved_id, saved_hash in entries:
            if saved_id == entry_id and saved_hash != digest:
                raise ValueError("entry-id already exists with different content")
        if any(saved_id == entry_id or saved_hash == digest for saved_id, saved_hash in entries):
            return {"status": "already_exists", "path": str(note.resolve())}
        numbers = [int(x) for x in re.findall(r"(?m)^### (\d+)\. ", text)]
        number = max(numbers, default=0) + 1
        newline = "\r\n" if b"\r\n" in baseline else "\n"
        block = f"### {number}. {title}（{date.today().isoformat()} 新增）\n{marker}\n{body}\n\n"
        block = block.replace("\r\n", "\n").replace("\n", newline).encode("utf-8")
        index = len(text[:matches[0].start()].encode("utf-8"))
        result = baseline[:index] + block + baseline[index:]
        with tempfile.NamedTemporaryFile(dir=note.parent, prefix=".ai-sync-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(result)
            stream.flush()
            os.fsync(stream.fileno())
        if note.exists() != existed or (existed and note.read_bytes() != original):
            raise RuntimeError("Note changed during operation; retry after other editor finishes")
        os.replace(temporary, note)
        return {"status": "created", "path": str(note.resolve()), "number": number}
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        lock.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--body-file", required=True)
    parser.add_argument("--entry-id", required=True)
    parser.add_argument("--require-obsidian", action="store_true", help="Reject test or generic destinations when Obsidian was requested")
    args = parser.parse_args()
    try:
        config = read_config(args.config)
        validate_destination(config, args.require_obsidian)
        result = archive(config["note_path"], args.title, Path(args.body_file).read_text(encoding="utf-8-sig"), args.entry_id)
        print(json.dumps(result, ensure_ascii=False))
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f"Archive failed: {error}\n")


if __name__ == "__main__":
    main()
