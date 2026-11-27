#!/usr/bin/env python3
"""Compare a built kernel's exported symbol CRCs against the tree's GKI ABI.

A vendor module built against the stock kernel carries the CRC of every symbol
it imports; a missing symbol or a changed CRC stops it from loading.

ABI sources: STG text (6.1+: gki/aarch64/abi.stg, android/abi_gki_aarch64.stg)
and libabigail XML (5.10/5.15: android/abi_gki_aarch64.xml).
Built side: Module.symvers or vmlinux.symvers. vmlinux.symvers lacks every symbol a
GKI loadable module exports (bluetooth, can, zsmalloc...), so with it missing symbols
are not judged; CRCs of what vmlinux exports still are.

usage: kmi_check.py ABI SYMVERS [REPORT]
Prints one summary line on stdout; the symbol lists go to REPORT.
Exit 0 on any comparison, 2 when an input cannot be read or parsed.
"""
import fnmatch
import os
import re
import sys

STG_BLOCK = re.compile(r"^elf_symbol \{\n(.*?)^\}", re.M | re.S)
STG_FIELD = re.compile(r"^\s+(\w+): (.+)$", re.M)
XML_SYMBOL = re.compile(r"<elf-symbol\s([^>]*?)/?>")
XML_ATTR = re.compile(r"(\w[\w-]*)='([^']*)'")


def parse_abi(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    abi = {}
    if path.endswith(".xml"):
        for m in XML_SYMBOL.finditer(text):
            a = dict(XML_ATTR.findall(m.group(1)))
            if a.get("is-defined") == "yes" and a.get("crc", "").startswith("0x") and a.get("name"):
                abi[a["name"]] = int(a["crc"], 16)
    else:
        for m in STG_BLOCK.finditer(text):
            f = dict(STG_FIELD.findall(m.group(1)))
            name = f.get("name", "").strip().strip('"')
            crc = f.get("crc", "").strip()
            if f.get("is_defined", "").strip() == "true" and name and crc.startswith("0x"):
                abi[name] = int(crc, 16)
    return abi


def parse_symvers(path):
    built = {}
    for line in open(path, encoding="utf-8", errors="replace"):
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0].startswith("0x"):
            built[parts[1]] = int(parts[0], 16)
    return built


def load_benign(model):
    """Symbols whose CRC change is known not to matter for this model (kmi_benign.tsv)."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kmi_benign.tsv")
    out = {}
    if not model or not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        sym, globs, why = (line.rstrip("\n").split("\t") + ["", ""])[:3]
        if any(fnmatch.fnmatchcase(model, g.strip()) for g in globs.split(",")):
            out[sym] = why
    return out


def main():
    if len(sys.argv) < 3:
        print("usage: kmi_check.py ABI SYMVERS [REPORT]", file=sys.stderr)
        return 2
    try:
        abi = parse_abi(sys.argv[1])
        built = parse_symvers(sys.argv[2])
    except OSError as e:
        print(f"kmi_check: {e}", file=sys.stderr)
        return 2
    if not abi or not built:
        print(f"kmi_check: nothing parsed (abi={len(abi)} built={len(built)})", file=sys.stderr)
        return 2

    vmlinux_only = sys.argv[2].endswith("vmlinux.symvers")
    missing = [] if vmlinux_only else sorted(n for n in abi if n not in built)
    benign_ok = load_benign(os.environ.get("OP_MODEL", ""))
    allchanged = sorted((n, abi[n], built[n]) for n in abi if n in built and built[n] != abi[n])
    changed = [c for c in allchanged if c[0] not in benign_ok]
    benign = [c for c in allchanged if c[0] in benign_ok]

    lines = [f"ABI: {sys.argv[1]}", f"built: {sys.argv[2]}",
             f"{len(abi)} ABI symbols, {len(built)} exported, "
             + ("missing not judged (vmlinux.symvers), " if vmlinux_only else f"{len(missing)} missing, ")
             + f"{len(changed)} CRC changed"]
    if missing:
        lines += ["", "missing:"] + [f"  {n}" for n in missing]
    if benign:
        lines += ["", "CRC changed but not used by any stock module (kmi_benign.tsv):"] + [f"  {n}: 0x{a:08x} != 0x{b:08x}  # {benign_ok[n]}" for n, a, b in benign]
    if changed:
        lines += ["", "CRC changed (abi != built):"] + [f"  {n}: 0x{a:08x} != 0x{b:08x}" for n, a, b in changed]
    if len(sys.argv) > 3:
        with open(sys.argv[3], "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")

    checked = sum(1 for n in abi if n in built)
    note = f" · {len(benign)} not used ({', '.join(n for n, _, _ in benign)})" if benign else ""
    if vmlinux_only:
        print(f"{checked}/{len(abi)} ABI symbols in vmlinux · {len(changed)} CRC changed{note} (Image-only: module exports not built)")
    else:
        print(f"{len(abi)} ABI symbols · {len(missing)} missing · {len(changed)} CRC changed{note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
