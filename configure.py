#!/usr/bin/python3
"""Enable Codex's native terminal scrollback; no companion window or packages."""
import argparse
import copy
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile
import time
import tomllib


def render_preference(text, fullscreen):
    before = tomllib.loads(text)
    expected = copy.deepcopy(before)
    expected.setdefault("tui", {})["fullscreen_transcript"] = fullscreen
    value = "true" if fullscreen else "false"
    section = re.search(r"(?m)^\[tui\][ \t]*(?:#.*)?$", text)
    if section:
        next_section = re.search(r"(?m)^\s*\[", text[section.end():])
        end = section.end() + next_section.start() if next_section else len(text)
        body = text[section.end():end]
        assignment = re.compile(r"(?m)^[ \t]*fullscreen_transcript[ \t]*=.*$")
        if assignment.search(body):
            body = assignment.sub(f"fullscreen_transcript = {value}", body, count=1)
        else:
            body = f"\nfullscreen_transcript = {value}" + body
        result = text[:section.end()] + body + text[end:]
    else:
        result = text.rstrip() + f"\n\n[tui]\nfullscreen_transcript = {value}\n"
    if tomllib.loads(result) != expected:
        raise ValueError("Configuration structure was unexpected; no changes were written.")
    return result


def configure(path, fullscreen=False):
    original = path.read_text() if path.exists() else ""
    if tomllib.loads(original).get("tui", {}).get("fullscreen_transcript") is fullscreen:
        return None
    updated = render_preference(original, fullscreen)
    path.parent.mkdir(parents=True, exist_ok=True)
    backup = None
    mode = 0o600
    if path.exists():
        mode = stat.S_IMODE(path.stat().st_mode)
        backup = path.with_name(path.name + f".scrollbar-backup-{time.time_ns()}")
        shutil.copy2(path, backup)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, prefix=".scrollbar-", delete=False) as f:
            temp = Path(f.name)
            os.fchmod(f.fileno(), mode)
            f.write(updated)
            f.flush()
            os.fsync(f.fileno())
        if (path.read_text() if path.exists() else "") != original:
            raise RuntimeError("The config changed during setup; retry when Codex is idle.")
        os.replace(temp, path)
    finally:
        if temp and temp.exists():
            temp.unlink()
    return backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path.home() / ".codex/config.toml")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--apply", action="store_true", help="use terminal scrollback on the next Codex launch")
    actions.add_argument("--fullscreen", action="store_true", help="return to Codex fullscreen mode on the next launch")
    args = parser.parse_args()
    if not args.apply and not args.fullscreen:
        data = tomllib.loads(args.config.read_text()) if args.config.exists() else {}
        print("Saved fullscreen preference:", data.get("tui", {}).get("fullscreen_transcript", "not set"))
        print("Run with --apply to use the terminal's real scrollbar. No changes made.")
        return
    backup = configure(args.config, fullscreen=args.fullscreen)
    if backup:
        print("Backup:", backup)
    print("Saved display mode:", "Fullscreen" if args.fullscreen else "Terminal scrollback")
    print("Restart Codex to apply. Existing tasks are not stopped by this helper.")


if __name__ == "__main__":
    main()
