#!/usr/bin/env python3
"""Configure Codex CLI for the HS Offenburg AI Portal."""

from __future__ import annotations

import argparse
import getpass
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


BASE_URL = "https://ai-portal.hs-offenburg.de/litellm/v1"
KEY_PORTAL_URL = "https://ai-portal.hs-offenburg.de/student"
DEFAULT_PROFILE = "aiportal"
DEFAULT_MODEL = "EA1_Labor_GPT-5.5"


def toml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def prompt_for_key(use_gui: bool) -> str:
    message = (
        "Fuege deinen persoenlichen AI-Portal-API-Key ein.\n\n"
        f"Erstelle den Key zuerst hier:\n{KEY_PORTAL_URL}"
    )

    if use_gui:
        try:
            import tkinter as tk
            from tkinter import simpledialog

            root = tk.Tk()
            root.withdraw()
            key = simpledialog.askstring(
                "Codex AI-Portal-Setup",
                message,
                show="*",
                parent=root,
            )
            root.destroy()
            if key:
                return key.strip()
        except Exception:
            pass

    print(f"Erstelle deinen persoenlichen API-Key hier: {KEY_PORTAL_URL}")
    return getpass.getpass("AI-Portal-API-Key: ").strip()


def prompt_for_model(default_model: str, use_gui: bool) -> str:
    if use_gui:
        try:
            import tkinter as tk
            from tkinter import simpledialog

            root = tk.Tk()
            root.withdraw()
            model = simpledialog.askstring(
                "Codex AI-Portal-Setup",
                "Modellname:",
                initialvalue=default_model,
                parent=root,
            )
            root.destroy()
            if model:
                return model.strip()
        except Exception:
            pass

    model = input(f"Modellname [{default_model}]: ").strip()
    return model or default_model


def backup_file(path: Path) -> None:
    if not path.exists():
        return

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_name(f"{path.name}.bak-{timestamp}")
    shutil.copy2(path, backup)
    print(f"Backup erstellt: {backup}")


def protect_file(path: Path) -> None:
    try:
        path.chmod(0o600)
    except OSError:
        pass


def replace_table(text: str, table_name: str, replacement: str) -> str:
    pattern = re.compile(
        rf"(?ms)^\[{re.escape(table_name)}\]\n.*?(?=^\[|\Z)"
    )
    match = pattern.search(text)

    if match:
        separator = "\n" if match.end() == len(text) else "\n\n"
        return (
            text[: match.start()]
            + replacement.rstrip()
            + separator
            + text[match.end() :]
        )

    if text and not text.endswith("\n"):
        text += "\n"
    if text and not text.endswith("\n\n"):
        text += "\n"
    return text + replacement.rstrip() + "\n"


def write_base_config(codex_home: Path, key: str) -> None:
    config_path = codex_home / "config.toml"
    codex_home.mkdir(parents=True, exist_ok=True)

    text = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    provider_block = f"""[model_providers.aiportal]
name = "HS Offenburg AI Portal"
base_url = "{BASE_URL}"
experimental_bearer_token = {toml_quote(key)}
wire_api = "responses"
"""

    updated = replace_table(text, "model_providers.aiportal", provider_block)

    if updated != text:
        backup_file(config_path)
        config_path.write_text(updated, encoding="utf-8")
        print(f"Aktualisiert: {config_path}")
    else:
        print(f"Keine Aenderung notwendig: {config_path}")

    protect_file(config_path)


def write_profile(codex_home: Path, profile: str, model: str) -> Path:
    profile_path = codex_home / f"{profile}.config.toml"
    profile_text = f"""model_provider = "aiportal"
model = {toml_quote(model)}
model_reasoning_effort = "high"
"""

    old = profile_path.read_text(encoding="utf-8") if profile_path.exists() else ""
    if old != profile_text:
        backup_file(profile_path)
        profile_path.write_text(profile_text, encoding="utf-8")
        print(f"Aktualisiert: {profile_path}")
    else:
        print(f"Keine Aenderung notwendig: {profile_path}")

    protect_file(profile_path)
    return profile_path


def launch_codex(profile: str) -> int:
    codex = shutil.which("codex")
    if not codex:
        print("Codex CLI wurde nicht im PATH gefunden. Starte es spaeter mit:")
        print(f"  codex -p {profile}")
        return 0

    print(f"Starte: codex -p {profile}")
    return subprocess.call([codex, "-p", profile])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Richtet Codex CLI fuer das HS Offenburg AI Portal ein."
    )
    parser.add_argument(
        "--codex-home",
        default=None,
        help="Codex-Verzeichnis. Standard: CODEX_HOME oder ~/.codex.",
    )
    parser.add_argument(
        "--profile",
        default=DEFAULT_PROFILE,
        help=f"Zu erstellendes Profil. Standard: {DEFAULT_PROFILE}",
    )
    parser.add_argument(
        "--model",
        default=None,
        help=f"Zu verwendendes Modell. Standard: {DEFAULT_MODEL}",
    )
    parser.add_argument(
        "--key",
        default=None,
        help="API-Key. Wenn er fehlt, fragt das Skript danach.",
    )
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Terminaleingabe statt eines kleinen Dialogfensters verwenden.",
    )
    parser.add_argument(
        "--no-launch",
        action="store_true",
        help="Nur die Konfiguration schreiben und Codex nicht starten.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.codex_home:
        codex_home = Path(args.codex_home).expanduser()
    else:
        import os

        codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()

    key = (args.key or "").strip()
    if not key:
        key = prompt_for_key(use_gui=not args.no_gui)

    if not key:
        print("Kein API-Key eingegeben. Abbruch.", file=sys.stderr)
        return 2

    model = (args.model or "").strip()
    if not model:
        model = prompt_for_model(DEFAULT_MODEL, use_gui=not args.no_gui)

    if not model:
        print("Kein Modell eingegeben. Abbruch.", file=sys.stderr)
        return 2

    write_base_config(codex_home, key)
    write_profile(codex_home, args.profile, model)

    print()
    print("Setup abgeschlossen.")
    print(f"Profil starten mit: codex -p {args.profile}")

    if args.no_launch:
        return 0

    return launch_codex(args.profile)


if __name__ == "__main__":
    raise SystemExit(main())
