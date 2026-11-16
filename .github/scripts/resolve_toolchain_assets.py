#!/usr/bin/env python3
"""Resolve the toolchain mirror assets that the configs under configs/ require.

Shared by two workflows so the "what do we need?" answer can never drift:

  * mirror-toolchains.yml -- `--format matrix`, the set to download and upload.
  * clean-up.yml          -- `--format json`, the set to KEEP when pruning the
                             `toolchain-cache` release.

Each config names a repo manifest that pins every prebuilt by revision, and the
mirror asset name is derived purely from (toolchain type, revision), so this
set is reproducible without touching the release at all. Callers diff it
against the live asset list themselves.

A config whose manifest cannot be fetched or parsed is reported in `failures`
and counted in `failed`. It is NOT fatal here, because the mirror can still
usefully mirror everything else -- but a pruner MUST refuse to delete anything
while `failed > 0`, since an unresolved config's toolchains are
indistinguishable from orphans.
"""

import argparse
import json
import shutil
import subprocess
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

# Substring of the manifest project name -> mirror asset prefix.
TOOLCHAIN_MAP = {
    "clang/host/linux-x86": "clang",
    "prebuilts/clang/host/linux-x86": "clang",
    "prebuilts/rust": "rust",
    "prebuilts/clang-tools": "clang-tools",
    "prebuilts/build-tools": "build-tools",
    "prebuilts/kernel-build-tools": "kernel-build-tools",
    "AnyKernel3": "AnyKernel3",
}

ONEPLUS_MANIFEST_BASE = (
    "https://raw.githubusercontent.com/OnePlusOSS/kernel_manifest/refs/heads"
)


def sanitize_filename(value):
    return (
        value.replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
        .replace("@", "_")
        .replace(" ", "_")
    )


def normalize_fetch_url(fetch):
    return fetch.rstrip("/") if fetch else ""


def build_project_url(base_url, project_name):
    return f"{base_url.rstrip('/')}/{project_name.strip('/')}"


def build_archive_url(base_url, project_name, rev):
    project_url = build_project_url(base_url, project_name)
    encoded_rev = urllib.parse.quote(rev, safe="")

    if "googlesource.com" in project_url:
        return f"{project_url}/+archive/{encoded_rev}.tar.gz"

    if "github.com" in project_url:
        return f"{project_url}/archive/{encoded_rev}.tar.gz"

    if "git.codelinaro.org" in project_url or "gitlab.com" in project_url:
        archive_name = Path(project_name).name
        return (
            f"{project_url}/-/archive/{encoded_rev}/{archive_name}-{encoded_rev}.tar.gz"
        )

    raise ValueError(f"Unknown toolchain provider for: {project_url}")


def load_configs(configs_dir):
    """Flatten every configs/**/*.json into one list. Invalid JSON is fatal."""
    files = sorted(Path(configs_dir).rglob("*.json"))

    if not files:
        print(f"::error::No JSON config files found under {configs_dir}/", file=sys.stderr)
        sys.exit(1)

    configs = []
    bad_files = []

    for file in files:
        try:
            text = file.read_text(encoding="utf-8-sig")

            if not text.strip():
                bad_files.append((str(file), "File is empty"))
                continue

            data = json.loads(text)

            if isinstance(data, list):
                configs.extend(data)
            elif isinstance(data, dict):
                configs.append(data)
            else:
                bad_files.append(
                    (
                        str(file),
                        f"Top-level JSON must be object or array, got {type(data).__name__}",
                    )
                )
        except json.JSONDecodeError as e:
            bad_files.append(
                (str(file), f"JSON decode error at line {e.lineno}, column {e.colno}: {e.msg}")
            )
        except Exception as e:  # noqa: BLE001 - surfaced to the workflow log
            bad_files.append((str(file), str(e)))

    if bad_files:
        print("::error::Invalid JSON config file(s) found", file=sys.stderr)
        for file, error in bad_files:
            print(f"::error file={file}::{error}", file=sys.stderr)
        sys.exit(1)

    print(f"Combined {len(configs)} config object(s) from {len(files)} file(s).", file=sys.stderr)
    return configs


def fetch_manifest(cfg, manifests_dir, dest):
    """Place the config's manifest XML at `dest`."""
    model = cfg.get("model", "Unknown")
    manifest = cfg.get("manifest", "")
    branch = cfg.get("branch", "")
    os_version = cfg.get("os_version", "").lower()

    if manifest.startswith("https://"):
        print(f"[{model}] Fetching manifest URL: {manifest}", file=sys.stderr)
        subprocess.run(
            ["curl", "-LfsS", "--retry", "3", "-o", str(dest), manifest], check=True
        )
        return

    if branch.startswith("wild/"):
        local_manifest = Path(manifests_dir) / os_version / manifest
        print(f"[{model}] Using local manifest: {local_manifest}", file=sys.stderr)
        if not local_manifest.exists():
            raise FileNotFoundError(f"Local manifest not found: {local_manifest}")
        shutil.copy(str(local_manifest), str(dest))
        return

    url = f"{ONEPLUS_MANIFEST_BASE}/{branch}/{manifest}"
    print(f"[{model}] Fetching OnePlus manifest: {url}", file=sys.stderr)
    subprocess.run(["curl", "-LfsS", "--retry", "3", "-o", str(dest), url], check=True)


def resolve(configs, manifests_dir, workdir):
    unique = {}
    failures = []
    processed = 0
    xml_file = Path(workdir) / "temp_manifest.xml"

    for cfg in configs:
        model = cfg.get("model", "Unknown")
        manifest = cfg.get("manifest", "")
        os_version_raw = cfg.get("os_version", "")

        if not manifest:
            failures.append({"model": model, "manifest": "", "error": "Missing manifest"})
            continue

        try:
            fetch_manifest(cfg, manifests_dir, xml_file)
            root = ET.parse(str(xml_file)).getroot()

            remotes = {}
            for remote in root.findall("remote"):
                name = remote.get("name")
                fetch = remote.get("fetch")
                if name and fetch:
                    remotes[name] = normalize_fetch_url(fetch)

            default = root.find("default")
            def_remote = default.get("remote") if default is not None else None
            def_rev = default.get("revision") if default is not None else None

            for project in root.findall("project"):
                name = project.get("name")
                if not name:
                    continue

                type_label = None
                for repo_key, label in TOOLCHAIN_MAP.items():
                    if repo_key in name:
                        type_label = label
                        break

                if not type_label:
                    continue

                remote_name = project.get("remote", def_remote)
                rev = project.get("revision", def_rev)

                if not remote_name or not rev:
                    print(
                        f"Skipping '{name}': remote or revision cannot be resolved.",
                        file=sys.stderr,
                    )
                    continue

                base_url = remotes.get(remote_name, "").rstrip("/")
                if not base_url:
                    print(
                        f"Skipping '{name}': remote '{remote_name}' has no fetch URL.",
                        file=sys.stderr,
                    )
                    continue

                cache_filename = f"{type_label}-{sanitize_filename(rev)}.tar.gz"

                if cache_filename in unique:
                    continue

                unique[cache_filename] = {
                    "rev": rev,
                    "url": build_archive_url(base_url, name, rev),
                    "name": name,
                    "type_label": type_label,
                    "cache_file": cache_filename,
                }
                print(
                    f"[{model}][{os_version_raw}] {type_label}: {rev}",
                    file=sys.stderr,
                )

            processed += 1
        except Exception as e:  # noqa: BLE001 - recorded, not fatal
            failures.append({"model": model, "manifest": manifest, "error": str(e)})
            print(
                f"::warning::Failed to process manifest '{manifest}' for {model}: {e}",
                file=sys.stderr,
            )

    return unique, processed, failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--configs-dir", default="configs")
    parser.add_argument("--manifests-dir", default="manifests")
    parser.add_argument("--workdir", default=".")
    parser.add_argument("--format", choices=("json", "matrix", "names"), default="json")
    parser.add_argument("--output", default="-", help="'-' for stdout")
    args = parser.parse_args()

    configs = load_configs(args.configs_dir)
    unique, processed, failures = resolve(configs, args.manifests_dir, args.workdir)

    result = {
        "assets": sorted(unique),
        "matrix": {"include": list(unique.values())},
        "count": len(unique),
        "processed": processed,
        "failed": len(failures),
        "failures": failures,
    }

    if args.format == "matrix":
        payload = json.dumps(result["matrix"], separators=(",", ":"))
    elif args.format == "names":
        payload = "\n".join(result["assets"])
    else:
        payload = json.dumps(result, separators=(",", ":"))

    if args.output == "-":
        print(payload)
    else:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")

    print("-" * 70, file=sys.stderr)
    print(f"Processed configs: {processed}", file=sys.stderr)
    print(f"Failed configs:    {len(failures)}", file=sys.stderr)
    print(f"Unique toolchains: {len(unique)}", file=sys.stderr)

    if not unique:
        print("::warning::No toolchain projects resolved.", file=sys.stderr)


if __name__ == "__main__":
    main()
