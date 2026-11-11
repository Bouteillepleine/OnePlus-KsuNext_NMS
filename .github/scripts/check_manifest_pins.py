#!/usr/bin/env python3
"""Report manifests whose pinned SHA has fallen behind the branch it tracks.

Consumes the state file oplus-kernel-monitor already maintains
({repo: {branch: "SHA|KERNEL"}}), so a normal run costs zero API calls: a pin
that matches its branch head is settled by a dictionary lookup.

The branch a SHA came from is not recoverable from the SHA, so each pinned
OnePlus project carries upstream="refs/heads/<branch>". `repo` ignores that
attribute when revision= is a SHA -- the CLO prebuilts already rely on the same
thing -- so it is inert for the build and authoritative for this check.

A manifest whose FILENAME carries a sublevel (oneplus_13r_6.1.118_w.xml) is
frozen there on purpose -- falling behind is the whole point of it, so it is
only reported when the branch moves WITHIN that sublevel. Everything else is a
base manifest and is expected to track its branch. Getting this wrong is not
cosmetic: the first version of this check reported all 28 frozen configs as
"the sublevel moved under us" on every run, which is precisely the noise that
trains you to stop reading the report.

Two outcomes, deliberately weighted differently:

  * the branch head moved but SUBLEVEL did not -- vendor/devicetree churn. Worth
    knowing, not worth waking anyone.
  * SUBLEVEL moved -- the case that matters. OnePlus' published 6.1 source
    reorders task_struct's ANDROID_KABI slots from .157 (see
    scripts/fix_oplus_task_struct_kabi.py), so a device crossing a sublevel is a
    device entering that blast radius. CRCs cannot see it and neither can a
    green build; only this can.

Only drifted pins cost an API call, to read SUBLEVEL at the pinned SHA.
"""

import glob
import json
import os
import re
import subprocess
import sys

PINNED_IN_NAME = re.compile(r"_(\d+\.\d+\.\d+)_")

PROJECT = re.compile(
    r'name="(android_kernel[a-z0-9_.]*oneplus_[a-z0-9]+)"[^>]*'
    r'revision="([0-9a-f]{40})"[^>]*upstream="refs/heads/([^"]+)"'
)
# upstream= may precede revision= depending on who last edited the manifest
PROJECT_ALT = re.compile(
    r'name="(android_kernel[a-z0-9_.]*oneplus_[a-z0-9]+)"[^>]*'
    r'upstream="refs/heads/([^"]+)"[^>]*revision="([0-9a-f]{40})"'
)


def gh(path, jq=None):
    cmd = ["gh", "api", path] + (["-q", jq] if jq else [])
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def sublevel_at(repo, ref):
    import base64
    c = gh("repos/OnePlusOSS/%s/contents/Makefile?ref=%s" % (repo, ref), ".content")
    if not c:
        return None
    try:
        t = base64.b64decode(c).decode("utf-8", "replace")
    except Exception:
        return None
    g = lambda k: (re.search(r"^%s\s*=\s*(\d+)" % k, t, re.M) or [None, "?"])[1]
    return "%s.%s.%s" % (g("VERSION"), g("PATCHLEVEL"), g("SUBLEVEL"))


def main():
    cfg_dir, man_dir, state_file = sys.argv[1], sys.argv[2], sys.argv[3]
    try:
        state = json.load(open(state_file))
    except Exception as e:
        print("::warning::manifest pin check skipped: cannot read %s (%s)" % (state_file, e))
        return 0

    wanted = set()
    for p in glob.glob(os.path.join(cfg_dir, "*.json")):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        if d.get("NMS") and d.get("manifest"):
            wanted.add(d["manifest"])

    moved, churn, unpinned = [], [], []
    for p in sorted(glob.glob(os.path.join(man_dir, "*.xml"))):
        name = os.path.basename(p)
        if name not in wanted:
            continue
        s = open(p, encoding="utf-8", errors="replace").read()
        hits = [(m.group(1), m.group(2), m.group(3)) for m in PROJECT.finditer(s)]
        hits += [(m.group(1), m.group(3), m.group(2)) for m in PROJECT_ALT.finditer(s)]
        if not hits:
            if re.search(r'name="android_kernel[a-z0-9_.]*oneplus_[a-z0-9]+"[^>]*revision="[0-9a-f]{40}"', s):
                unpinned.append(name)
            continue
        for repo, sha, branch in hits:
            entry = state.get(repo, {}).get(branch)
            if not entry:
                continue
            tip_sha, _, tip_kv = entry.partition("|")
            if tip_sha == sha:
                continue
            frozen = PINNED_IN_NAME.search(name)
            if frozen and tip_kv != frozen.group(1):
                # pinned to a sublevel the branch has since left: by design
                continue
            if "common" in repo or "_oneplus_mt" in repo:
                pinned_kv = sublevel_at(repo, sha) or "?"
            else:
                pinned_kv = tip_kv
            row = (name, repo, sha[:10], pinned_kv, tip_sha[:10], tip_kv, branch)
            (moved if pinned_kv != tip_kv else churn).append(row)

    out = []
    if moved:
        out.append("### ⚠️ Manifest pins: the SUBLEVEL moved under us\n")
        out.append("| Manifest | Pinned | Tip | Branch |\n| :--- | :--- | :--- | :--- |\n")
        for n, repo, s, pk, t, tk, b in moved:
            out.append("| `%s` | `%s` %s | `%s` **%s** | `%s` |\n" % (n, s, pk, t, tk, b))
        out.append("\nA 6.1 device crossing into .157 enters the `task_struct` KABI "
                   "slot blast radius; `fix_oplus_task_struct_kabi.py` is guarded on "
                   "the layout and follows automatically, but the move should be a "
                   "deliberate commit, not a surprise.\n\n")
    if churn:
        out.append("### \U0001f504 Manifest pins behind their branch (same SUBLEVEL)\n")
        out.append("| Manifest | Pinned | Tip | Branch |\n| :--- | :--- | :--- | :--- |\n")
        for n, repo, s, pk, t, tk, b in churn:
            out.append("| `%s` | `%s` | `%s` | `%s` |\n" % (n, s, t, b))
        out.append("\n")
    if unpinned:
        out.append("### ℹ️ Manifests with a SHA pin and no `upstream=`, so drift cannot be checked\n")
        out.append("".join("- `%s`\n" % n for n in unpinned) + "\n")

    body = "".join(out)
    sys.stdout.write(body)

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary and body:
        with open(summary, "a") as fh:
            fh.write("\n" + body)
    print("pin check: %d sublevel move(s), %d same-sublevel drift(s), %d unpinned"
          % (len(moved), len(churn), len(unpinned)), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
