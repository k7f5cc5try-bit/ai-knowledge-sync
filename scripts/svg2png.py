"""Render self-contained SVG using a local Chromium browser, without overwriting images."""
import argparse
from datetime import date
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile
import uuid
import xml.etree.ElementTree as ET
import zlib
from common import read_config


def validate_svg(source):
    text = Path(source).read_text(encoding="utf-8-sig")
    if re.search(r"<!DOCTYPE|<!ENTITY|var\s*\(|@import", text, re.I):
        raise ValueError("SVG must have no DTD, entities, unresolved CSS variables or imports")
    root = ET.fromstring(text)
    if root.tag.split("}")[-1] != "svg":
        raise ValueError("Source is not SVG")
    for node in root.iter():
        if node.tag.split("}")[-1].lower() in ("script", "foreignobject", "animate", "animatetransform", "set"):
            raise ValueError("Only static self-contained SVG is supported")
        for key, value in node.attrib.items():
            name = key.split("}")[-1].lower()
            if name.startswith("on") or (name in ("href", "src", "base") and not value.startswith("#")):
                raise ValueError("Event handlers and external resource references are unsupported")
    for value in re.findall(r"url\s*\((.*?)\)", text, re.I | re.S):
        if not value.strip().strip("\"'").startswith("#"):
            raise ValueError("External CSS resources are unsupported")
    return text


def check_png(path, expected):
    data = Path(path).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Browser did not produce a PNG")
    offset, dimensions, compressed, ended = 8, None, [], False
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError("Truncated PNG")
        size = struct.unpack(">I", data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + size]
        crc = data[offset + 8 + size:offset + 12 + size]
        if len(crc) != 4 or zlib.crc32(kind + payload) != struct.unpack(">I", crc)[0]:
            raise ValueError("PNG checksum mismatch")
        if kind == b"IHDR":
            dimensions = struct.unpack(">II", payload[:8])
        if kind == b"IDAT":
            compressed.append(payload)
        if kind == b"IEND":
            ended = True
            break
        offset += size + 12
    if dimensions != expected or not ended or not compressed:
        raise ValueError(f"Incomplete PNG or incorrect dimensions: {dimensions}, expected {expected}")
    if not zlib.decompress(b"".join(compressed)):
        raise ValueError("Empty PNG pixel data")


def find_browser(configured):
    if configured:
        if Path(configured).is_file():
            return configured
        raise ValueError("Configured browser_path does not exist")
    candidates = []
    for base in (os.environ.get("PROGRAMFILES"), os.environ.get("PROGRAMFILES(X86)"), os.environ.get("LOCALAPPDATA")):
        if base:
            candidates.extend([str(Path(base) / "Google/Chrome/Application/chrome.exe"), str(Path(base) / "Microsoft/Edge/Application/msedge.exe")])
    candidates.extend(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"])
    candidates.extend(filter(None, (shutil.which(name) for name in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge"))))
    for candidate in candidates:
        if Path(candidate).is_file():
            return candidate
    raise ValueError("Chrome/Edge not found; set browser_path in configuration")


def convert(source, destination, topic, width, height, scale, browser):
    if not (1 <= width <= 4096 and 1 <= height <= 4096 and scale in (1, 2)):
        raise ValueError("Width/height must be 1..4096 and scale must be 1 or 2")
    svg = validate_svg(source)
    with tempfile.TemporaryDirectory(prefix="ai-sync-") as folder:
        work = Path(folder)
        (work / "source.svg").write_text(svg, encoding="utf-8")
        (work / "index.html").write_text(f'<!doctype html><meta charset="utf-8"><style>html,body{{margin:0;padding:0;width:{width}px;height:{height}px;overflow:hidden}}img{{display:block;width:{width}px;height:{height}px}}</style><img src="source.svg">', encoding="utf-8")
        output = work / "render.png"
        command = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run", "--no-default-browser-check", f"--user-data-dir={work / 'profile'}", f"--force-device-scale-factor={scale}", f"--window-size={width},{height}", "--virtual-time-budget=1000", f"--screenshot={output}", (work / "index.html").as_uri()]
        process = subprocess.run(command, capture_output=True, timeout=45, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if process.returncode != 0:
            raise RuntimeError(f"Browser exited with code {process.returncode}")
        check_png(output, (width * scale, height * scale))
        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=True)
        name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "-", topic).strip(" .")[:60] or "diagram"
        target = destination / f"{date.today().isoformat()}-{name}-{uuid.uuid4().hex[:12]}.png"
        created = False
        try:
            with target.open("xb") as stream:
                created = True
                stream.write(output.read_bytes())
        except OSError:
            if created:
                target.unlink(missing_ok=True)
            raise
        return target.resolve()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("config", "source", "topic"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--scale", type=int, default=2)
    args = parser.parse_args()
    try:
        config = read_config(args.config)
        output = convert(args.source, config["image_dir"], args.topic, args.width, args.height, args.scale, find_browser(config.get("browser_path")))
        print(f"Saved PNG: {output}")
    except (OSError, ValueError, RuntimeError, ET.ParseError, subprocess.TimeoutExpired, zlib.error) as error:
        parser.exit(1, f"Conversion failed: {error}\n")


if __name__ == "__main__":
    main()
