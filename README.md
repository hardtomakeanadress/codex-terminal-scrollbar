# Codex terminal scrollbar

Use your terminal's **real, draggable scrollbar** with Codex CLI. No floating panel, custom Codex build, new desktop app, or extra Python packages.

Codex 0.164.0 has two transcript modes. In fullscreen mode, Codex owns the screen and conversation scrolling. In Scrollback mode, the terminal owns scrollback, so its scrollbar can move through long answers. This project is a small configuration helper for the built-in mode, not an implementation of a new scrollbar.

## Enable

```sh
python3 configure.py --apply
```

The helper backs up `~/.codex/config.toml`, preserves the other settings, and sets:

```toml
[tui]
fullscreen_transcript = false
alternate_screen = "never"
```

Both settings are needed: disabling fullscreen transcript ownership alone leaves
the default alternate screen enabled in GNOME Terminal, preventing native scrollback.

Then exit the interactive Codex CLI with `/quit` and resume your task:

```sh
codex resume --last
```

If another task has become the most recent, use `codex resume` and select the correct task instead. A running voice conversation ends when the CLI exits; start `/voice` again after resuming. The helper itself does not stop your CLI or voice session.

Codex's `/tui` menu saves the transcript preference only; it does not disable the
alternate screen. For a single launch without changing preferences:

```sh
codex --no-alt-screen resume --last
```

## GNOME Terminal

In Preferences, select your profile, open Scrolling, and enable **Show scrollbar**. Use enough scrollback history for your conversations, or enable unlimited scrollback if appropriate for your machine.

The scrollbar is at the terminal's right edge. Drag its thumb to move through the terminal's history. This changes the entire terminal viewport; it does not keep the Codex composer pinned onscreen while you browse older output. You may need to scroll back to the bottom to see the current prompt. Modal screens may behave differently.

## Undo

```sh
python3 configure.py --fullscreen
```

This sets `fullscreen_transcript = true` and returns `alternate_screen` to its
default `"auto"` policy. Restart Codex again. Original configuration backups stay
next to the config file and may contain private settings; do not publish them.

## Scope and verification

- Python 3.11+ (standard library only).
- Targets Codex CLI 0.164.0; future versions may change the preference.
- Checked against the original [mode-picker implementation](https://github.com/openai/codex/blob/rust-v0.164.0/codex-rs/tui/src/app/tui_mode_picker.rs), [startup mode resolution](https://github.com/openai/codex/blob/rust-v0.164.0/codex-rs/tui/src/lib.rs), and [transcript ownership rules](https://github.com/openai/codex/blob/rust-v0.164.0/codex-rs/tui/src/transcript_mode.rs).
- Configuration checks verify that unrelated TOML settings survive, backups contain the original content, file permissions are preserved, and repeated setup makes no extra backup.
- No network access, telemetry, microphone access, package installation, shell startup edits, or background processes.
- The active-session UI change can only be confirmed after restarting Codex. Source verification and configuration validation do not substitute for that live check.

Run the configuration checks:

```sh
python3 tests/config_check.py
```

Independent project, not affiliated with OpenAI or GNOME. MIT license.
