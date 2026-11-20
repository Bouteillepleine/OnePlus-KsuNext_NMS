import os, re, sys
from collections import OrderedDict

root = sys.argv[1]
order = ["5.10", "5.15", "6.1", "6.6", "6.12"]
kmis = [k for k in order if os.path.isdir(os.path.join(root, k))]
rows = OrderedDict()

def add(cve, subj, kmi):
    e = rows.setdefault(cve, [subj, []])
    if kmi not in e[1]:
        e[1].append(kmi)

def subject(path):
    with open(path, errors="ignore") as f:
        lines = f.read().split("\n")
    for i, line in enumerate(lines):
        if line.startswith("Subject:"):
            s = line[8:].strip()
            for cont in lines[i + 1:]:
                if not cont.startswith((" ", "\t")):
                    break
                s += " " + cont.strip()
            return re.sub(r"^\[PATCH[^\]]*\]\s*", "", s)
    return ""

for k in kmis:
    for fn in sorted(os.listdir(os.path.join(root, k))):
        m = re.match(r"^\d{4}-(CVE-\d+-\d+)\.patch$", fn)
        if m:
            add(m.group(1), subject(os.path.join(root, k, fn)), k)
for fn in sorted(os.listdir(root)):
    m = re.match(r"^cve-(\d+)-(\d+)-.*-full\.patch$", fn)
    if m:
        add(f"CVE-{m.group(1)}-{m.group(2)}", subject(os.path.join(root, fn)), "6.12")

def key(c):
    y, n = c.split("-")[1:]
    return (int(y), int(n))

print("| CVE | Fix | Kernels |")
print("|---|---|---|")
for cve in sorted(rows, key=key):
    subj, ks = rows[cve]
    ks = [k for k in order if k in ks]
    subj = subj.replace("|", "\\|")
    print(f"| [{cve}](https://nvd.nist.gov/vuln/detail/{cve}) | {subj} | {' · '.join(ks)} |")
