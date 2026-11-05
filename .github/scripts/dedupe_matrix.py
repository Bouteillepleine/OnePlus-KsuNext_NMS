#!/usr/bin/env python3
"""Drop build legs that would produce a zip some other leg already produces.

The AK3 name is AK3_<base model>_<os>_<VERSION.PATCHLEVEL.SUBLEVEL>_..., and
ZIP_MODEL strips the -X.Y.Z suffix off the config's model on purpose: the file
names the device and the kernel it carries, not which config built it. So two
configs for one device that resolve to the same sublevel are the same
deliverable. They collide on the artifact name, one upload silently replaces the
other, and a 25-minute build is spent for nothing.

That is not hypothetical: OP-NORD-4's unpinned branch tip is exactly the sha
OP-NORD-4-6.1.157 pins, so run 41434571727 had 82 legs and 81 zips.

Keep the pinned config (a sha, reproducible) over the unpinned one (a branch,
which moves on without warning). Resolution is fail-open: a leg whose sublevel
cannot be read is kept, because a duplicate build costs CI minutes while a
wrongly dropped one costs a device its kernel.
"""

import argparse
import base64
import concurrent.futures
import json
import os
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

PINNED_SUFFIX = re.compile(r"-\d+\.\d+\.\d+$")
KERNEL_PATH = re.compile(r"^(kernel_platform/common|kernel-\d+\.\d+)$")
MAKEFILE_VARS = re.compile(
    r"^(VERSION|PATCHLEVEL|SUBLEVEL)\s*=\s*(\d+)\s*$", re.MULTILINE
)


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def kernel_project(manifest_path):
    """The (fetch_base, repo, revision) of the manifest's kernel source."""
    root = ET.parse(manifest_path).getroot()
    remotes = {
        r.get("name"): (r.get("fetch") or "").rstrip("/")
        for r in root.findall("remote")
    }
    for project in root.findall("project"):
        if not KERNEL_PATH.match(project.get("path") or ""):
            continue
        fetch = remotes.get(project.get("remote"), "")
        if not any(h in fetch for h in ("github.com", "googlesource.com")):
            return None  # nothing we know how to read a single file from
        return fetch, project.get("name"), project.get("revision")
    return None


def makefile_head(fetch, repo, revision):
    """The first lines of the Makefile at revision, or None.

    The OnePlus trees live on github and serve files raw; the GKI manifests take
    kernel/common from googlesource, whose gitiles only serves base64.
    """
    if "googlesource.com" in fetch:
        url = "%s/%s/+/%s/Makefile?format=TEXT" % (fetch, repo, revision)
        with urllib.request.urlopen(url, timeout=30) as r:
            return base64.b64decode(r.read()).decode("utf-8", "replace")
    owner = fetch.rsplit("/", 1)[-1]
    url = "https://raw.githubusercontent.com/%s/%s/%s/Makefile" % (owner, repo, revision)
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read(8192).decode("utf-8", "replace")


def fetch_sublevel(fetch, repo, revision):
    """VERSION.PATCHLEVEL.SUBLEVEL from the Makefile at revision, or None."""
    for attempt in range(3):
        try:
            found = dict(MAKEFILE_VARS.findall(makefile_head(fetch, repo, revision)))
            if {"VERSION", "PATCHLEVEL", "SUBLEVEL"} <= set(found):
                return "%s.%s.%s" % (
                    found["VERSION"],
                    found["PATCHLEVEL"],
                    found["SUBLEVEL"],
                )
            return None
        except (urllib.error.URLError, OSError, ValueError):
            if attempt == 2:
                return None
    return None


def resolve(entry, manifests_dir, cache):
    name = entry.get("manifest") or ""
    path = os.path.join(manifests_dir, (entry.get("os_version") or "").lower(), name)
    if not os.path.isfile(path):
        return None, "no manifest file at %s" % path
    try:
        project = kernel_project(path)
    except ET.ParseError as e:
        return None, "unparsable manifest: %s" % e
    if not project:
        return None, "no resolvable kernel-source project in %s" % name
    if project in cache:
        return cache[project], None
    sublevel = fetch_sublevel(*project)
    cache[project] = sublevel
    if not sublevel:
        return None, "could not read Makefile at %s/%s@%s" % project
    return sublevel, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("matrix", help="JSON array of config entries")
    ap.add_argument("-o", "--out", help="where to write the kept entries (default: stdout)")
    ap.add_argument("--manifests", default="manifests")
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()

    entries = json.load(open(args.matrix))
    if not isinstance(entries, list):
        log("::error::%s does not hold a JSON array" % args.matrix)
        return 1

    cache = {}
    # Warm the cache in parallel; each distinct (repo, revision) is fetched once.
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        wanted = {}
        for e in entries:
            name = e.get("manifest") or ""
            path = os.path.join(
                args.manifests, (e.get("os_version") or "").lower(), name
            )
            if not os.path.isfile(path):
                continue
            try:
                project = kernel_project(path)
            except ET.ParseError:
                continue
            if project and project not in wanted:
                wanted[project] = pool.submit(fetch_sublevel, *project)
        for project, future in wanted.items():
            cache[project] = future.result()

    resolved, unresolved = [], []
    for e in entries:
        sublevel, why = resolve(e, args.manifests, cache)
        base = PINNED_SUFFIX.sub("", e.get("model") or "")
        resolved.append(
            {
                "entry": e,
                "base": base,
                "pinned": base != (e.get("model") or ""),
                "sublevel": sublevel,
            }
        )
        if why:
            unresolved.append((e.get("model"), why))

    # Pinned configs claim their (device, kernel) first; an unpinned leg that
    # lands on a claimed pair is the redundant one.
    claimed = {}
    for r in resolved:
        if r["pinned"] and r["sublevel"]:
            claimed.setdefault((r["base"], r["sublevel"]), r["entry"].get("model"))

    kept, dropped = [], []
    for r in resolved:
        key = (r["base"], r["sublevel"])
        if not r["sublevel"]:
            kept.append(r["entry"])
            continue
        owner = claimed.get(key)
        model = r["entry"].get("model")
        if owner and owner != model:
            dropped.append((model, owner, r["sublevel"]))
            continue
        if not owner:
            claimed[key] = model
        kept.append(r["entry"])

    for model, why in unresolved:
        log("::warning::%s: kernel version unresolved (%s); keeping the leg" % (model, why))
    for model, owner, sublevel in dropped:
        log(
            "::notice::skipping %s: it builds %s, which %s already covers"
            % (model, sublevel, owner)
        )
    log("dedupe: %d legs in, %d kept, %d skipped" % (len(entries), len(kept), len(dropped)))

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary and (dropped or unresolved):
        with open(summary, "a") as fh:
            fh.write("\n### Matrix dedupe\n\n")
            if dropped:
                fh.write("| Skipped | Kernel | Already built by |\n|---|---|---|\n")
                for model, owner, sublevel in dropped:
                    fh.write("| `%s` | %s | `%s` |\n" % (model, sublevel, owner))
            for model, why in unresolved:
                fh.write("\n> `%s`: kernel version unresolved (%s) - leg kept.\n" % (model, why))

    out = json.dumps(kept, separators=(",", ":"))
    if args.out:
        open(args.out, "w").write(out)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
