#!/usr/bin/env python3
"""Validate the configs/ and manifests/ inventory."""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REQUIRED_FIELDS = (
    "model",
    "soc",
    "branch",
    "manifest",
    "android_version",
    "kernel_version",
    "os_version",
)


def check_configs(root: Path, errors: list[str]) -> None:
    config_dirs = sorted(p for p in (root / "configs").glob("a[0-9]*") if p.is_dir())
    if not config_dirs:
        errors.append("configs/ contains no aNN directories")

    seen: dict[tuple[str, str], Path] = {}

    for config_dir in config_dirs:
        expected_os = f"A{config_dir.name[1:]}"
        manifest_dir = root / "manifests" / config_dir.name
        configs = sorted(config_dir.glob("*.json"))
        if not configs:
            errors.append(f"{config_dir.relative_to(root).as_posix()} has no JSON configurations")

        for path in configs:
            rel = path.relative_to(root).as_posix()
            if path.is_symlink() or not path.is_file():
                errors.append(f"{rel}: not a regular file")
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append(f"{rel}: invalid JSON: {exc}")
                continue
            if not isinstance(data, dict):
                errors.append(f"{rel}: not a JSON object")
                continue

            for field in REQUIRED_FIELDS:
                value = data.get(field)
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"{rel}: {field} must be a non-empty string")

            if data.get("os_version") != expected_os:
                errors.append(f"{rel}: os_version must be {expected_os!r}")

            # set-op-model selects devices on .model, so it has to be the
            # filename and it has to be unique within an OS group.
            if data.get("model") != path.stem:
                errors.append(f"{rel}: model must be {path.stem!r}")
            identity = (str(data.get("os_version")), str(data.get("model")))
            if identity in seen:
                errors.append(
                    f"{rel}: duplicate os_version/model {identity!r}, already used by "
                    f"{seen[identity].relative_to(root).as_posix()}"
                )
            else:
                seen[identity] = path

            manifest = data.get("manifest")
            if (
                not isinstance(manifest, str)
                or not manifest.endswith(".xml")
                or Path(manifest).name != manifest
            ):
                errors.append(f"{rel}: manifest must be a local .xml filename")
            else:
                target = manifest_dir / manifest
                if target.is_symlink() or not target.is_file():
                    errors.append(f"{rel}: missing manifest {target.relative_to(root).as_posix()}")


def check_manifests(root: Path, errors: list[str]) -> int:
    paths = sorted((root / "manifests").glob("a[0-9]*/*.xml"))
    if not paths:
        errors.append("manifests/ contains no XML manifests")

    # kernel-source-sync resolves the mirror asset as {label}-{revision}.tar.gz,
    # so a stray AnyKernel3 revision misses the toolchain cache and only falls
    # back to a direct download on runs of four devices or fewer.
    ak3: dict[str, list[str]] = {}

    for path in paths:
        rel = path.relative_to(root).as_posix()
        if path.is_symlink() or not path.is_file():
            errors.append(f"{rel}: not a regular file")
            continue
        try:
            document = ET.parse(path)
        except Exception as exc:
            errors.append(f"{rel}: invalid XML: {exc}")
            continue
        if document.getroot().tag != "manifest":
            errors.append(f"{rel}: XML root must be <manifest>")
            continue
        for project in document.getroot().iter("project"):
            if project.get("name") == "AnyKernel3":
                ak3.setdefault(project.get("revision") or "<unset>", []).append(rel)

    if len(ak3) > 1:
        majority = max(ak3, key=lambda rev: len(ak3[rev]))
        for revision, users in sorted(ak3.items()):
            if revision == majority:
                continue
            for rel in users:
                errors.append(
                    f"{rel}: AnyKernel3 revision {revision!r} differs from "
                    f"{majority!r} used by {len(ak3[majority])} other manifest(s)"
                )

    return len(paths)


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    errors: list[str] = []

    check_configs(root, errors)
    manifest_count = check_manifests(root, errors)

    if errors:
        for error in errors:
            print(f"::error::{error}")
        print(f"{len(errors)} problem(s) found", file=sys.stderr)
        return 1

    config_count = sum(1 for _ in (root / "configs").glob("a[0-9]*/*.json"))
    print(f"validated {config_count} configurations and {manifest_count} manifests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
