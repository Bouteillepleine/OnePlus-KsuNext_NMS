<div align="center">

# OnePlus 📦 KernelSU Next 📦 NoMount

### A custom OnePlus kernel + a **mountless** hiding add-on

*Automated AnyKernel3 builds for dozens of OnePlus models — with `KernelSU Next` root and **NoMount** hookless VFS redirection baked in.*

[![Latest Release](https://img.shields.io/github/v/release/Bouteillepleine/OnePlus-KsuNext_NMS?style=for-the-badge&logo=github&label=Latest%20Release&color=6C4AB6)](https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/Bouteillepleine/OnePlus-KsuNext_NMS/total?style=for-the-badge&logo=icloud&logoColor=white&label=Downloads&color=2E8B57)](https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/releases)
[![Build](https://img.shields.io/github/actions/workflow/status/Bouteillepleine/OnePlus-KsuNext_NMS/build-kernel-release.yml?style=for-the-badge&logo=githubactions&logoColor=white&label=Build)](https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/actions)
[![Stars](https://img.shields.io/github/stars/Bouteillepleine/OnePlus-KsuNext_NMS?style=for-the-badge&logo=github&color=E3B341)](https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/stargazers)

**Based on [WildKernels/OnePlus_KernelSU_SUSFS](https://github.com/WildKernels/OnePlus_KernelSU_SUSFS)**

</div>

> [!WARNING]
> A custom kernel can disable hardware key-attestation, so **Google Wallet** tap-to-pay, Play Integrity **STRONG**, and some banking apps may stop working. Unlocking the bootloader **wipes your data**. Back up your stock `boot.img` first. Flash at your own risk.

---

## 🧩 It's a kernel **+** an add-on — two separate downloads

Every release contains **two things**. Flash the kernel first, then add NoMount Suite on top of it.

|  | 1️⃣ The kernel — *built here* | 2️⃣ NoMount Suite — *the add-on* |
|---|---|---|
| **What it is** | AnyKernel3 ZIP (`AK3_<device>_…zip`) with `KernelSU Next` root and `CONFIG_NOMOUNT=y` compiled in | `00_NoMount-Module-vX.Y.Z.zip` — the metamodule that switches NoMount **on** |
| **Where it comes from** | This repo's GitHub Actions — one ZIP per device | The separate **[NoMount Suite](https://github.com/Bouteillepleine/NoMount-Suite)** — attached to each release as an add-on (sorted to the top of the Assets list) |
| **How you install it** | Flash with **Kernel Flasher** or **KernelSU Next Manager** | **KernelSU Next Manager → Modules → Install from storage** |
| **Get it now** | [⬇️ Latest release](https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/releases/latest) | [⬇️ Latest release](https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/releases/latest) — it's at the top of the Assets list |

> [!IMPORTANT]
> **The kernel on its own does nothing visible.** NoMount is *compiled in* but stays **dormant** until the **NoMount Suite** module activates it. NoMount Suite is the part that carries your injection rules, the WebUI, and the spoofing — think of it like a Magisk/KSU module. **You need both.**

---

## 🫥 Why NoMount?

Most hiding solutions **mount** something — an `overlayfs` or bind mount — to swap files in. Every mount is a line in `/proc/mounts` and an `st_dev` mismatch a detector can read.

**NoMount serves your modules with _zero_ mounts.** It's a hookless, per-inode VFS redirection living inside the kernel:

- 🚫 **No overlay / bind mounts** — there's nothing in the mount table to find.
- 🎯 **Per-app, per-file** — redirect only the files you choose, only for the UIDs you choose.
- 🧼 **No mount-hiding cat-and-mouse** — you can't be caught hiding a mount that never existed.
- 🖥️ **WebUI-driven** — injection rules, per-app hiding and health checks, all from your manager.

<table>
  <tr>
    <td align="center"><a href="https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/blob/NoMount/docs/screenshots/status.jpg"><img src="https://raw.githubusercontent.com/Bouteillepleine/OnePlus-KsuNext_NMS/NoMount/docs/screenshots/status.jpg" width="155" alt="Status"></a></td>
    <td align="center"><a href="https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/blob/NoMount/docs/screenshots/modules.jpg"><img src="https://raw.githubusercontent.com/Bouteillepleine/OnePlus-KsuNext_NMS/NoMount/docs/screenshots/modules.jpg" width="155" alt="Modules"></a></td>
    <td align="center"><a href="https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/blob/NoMount/docs/screenshots/rules.jpg"><img src="https://raw.githubusercontent.com/Bouteillepleine/OnePlus-KsuNext_NMS/NoMount/docs/screenshots/rules.jpg" width="155" alt="Rules"></a></td>
    <td align="center"><a href="https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/blob/NoMount/docs/screenshots/check.jpg"><img src="https://raw.githubusercontent.com/Bouteillepleine/OnePlus-KsuNext_NMS/NoMount/docs/screenshots/check.jpg" width="155" alt="Check"></a></td>
    <td align="center"><a href="https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/blob/NoMount/docs/screenshots/duckdetector.jpg"><img src="https://raw.githubusercontent.com/Bouteillepleine/OnePlus-KsuNext_NMS/NoMount/docs/screenshots/duckdetector.jpg" width="155" alt="Duck Detector"></a></td>
  </tr>
  <tr>
    <td align="center"><sub><b>Status</b><br>zero mounts, live counts</sub></td>
    <td align="center"><sub><b>Modules</b><br>what is served, and how</sub></td>
    <td align="center"><sub><b>Rules</b><br>per-module rule breakdown</sub></td>
    <td align="center"><sub><b>Check</b><br>one diagnostic, plain verdicts</sub></td>
    <td align="center"><sub><b>Duck Detector</b><br>0 danger, 0 warning</sub></td>
  </tr>
</table>

<sub>Tap a screenshot for the full-size view.</sub>

---

## ✨ Features

- **KernelSU Next** — kernel-level root.
- **NoMount** — hookless VFS redirection; modules are served with **no mount at all**.
- **WireGuard** — modern VPN built into the kernel.
- **BBR & ECN** — TCP / network optimizations.
- **sched_ext** — extensible scheduler framework (supported kernels).

---

## 📱 Supported devices

One build fans out to **dozens** of OnePlus models across Android 13–16 and kernel 5.10–6.12.
See the [**latest release**](https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/releases/latest) for the full, per-device list — or browse:

```text
configs/
```

---

## 🚀 Installation

**Prerequisites:** unlocked bootloader · a backed-up stock `boot.img` · **[Kernel Flasher](https://github.com/fatalcoder524/KernelFlasher/releases)** installed.

1. **Download** the [latest release](https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/releases/latest) — grab **both**:
   - the **kernel** ZIP matching your exact device / OS / kernel base, and
   - the **`00_NoMount-Module-vX.Y.Z.zip`** add-on (top of the Assets list).
2. **Flash the kernel** ZIP with **Kernel Flasher** (or **KernelSU Next Manager**).
3. **Install the KernelSU Next Manager APK** — use the version shown as `KernelSU Next Version` in the release notes.
4. 🧩 **Add NoMount Suite:** KernelSU Next Manager → **Modules → Install from storage** → select `00_NoMount-Module-…zip`.
   > Already have a metamodule? Remove it and reboot **first** — only one metamodule can be active at a time.
5. **Reboot.**
6. Open **KernelSU Next Manager → NoMount Suite → Open** — the WebUI should show **Active** with your rules.

> [!TIP]
> **Safety net:** if the phone fails to boot **3 times** in a row, NoMount auto-disables itself so you can get back in and recover. Keep your stock `boot.img` handy either way.

---

## 🔄 Updating &amp; removing

- **Update** — re-flash the kernel ZIP **and** NoMount Suite together (keep them a matched set).
- **After an OTA** — the system update restores the stock kernel; just re-flash the release.
- **Remove** — delete NoMount Suite in KernelSU Next Manager and reboot, then flash a stock boot image (or take an OTA) to drop the custom kernel.

---

## ❓ FAQ

**Do I really need the module?** Yes. The kernel ships NoMount **dormant**; NoMount Suite activates it. No Suite → no hiding.

**Where does the module come from?** It's a **separate add-on**, maintained in the [NoMount Suite](https://github.com/Bouteillepleine/NoMount-Suite) and attached to each release as `00_NoMount-Module-vX.Y.Z.zip` (named to sort to the top of the Assets).

**Can I keep my current kernel and just flash the module?** No — NoMount must be compiled into the kernel (`CONFIG_NOMOUNT=y`). Use the kernel from this release.

**Will it pass Play Integrity / my bank?** NoMount removes the *mount* signal. It **cannot** restore **hardware** key-attestation, which a custom kernel may break (STRONG / Wallet). Always test with your own apps.

---

## 🛠️ Building it yourself

Via GitHub Actions:

```text
Actions → Build and Release OnePlus Kernels → Run workflow
```

Root option:

```json
[{"type":"KSUN","hash":"main"}]
```

> **First run:** enable **Force toolchain sync before build** (auto-on for releases) — required once to populate the toolchain cache.

---

## 🔗 Links

- [KernelSU Next](https://github.com/KernelSU-Next/KernelSU-Next) · [KernelSU Next Manager releases](https://github.com/KernelSU-Next/KernelSU-Next/releases)
- [NoMount Suite](https://github.com/Bouteillepleine/NoMount-Suite) — the hiding add-on
- [Kernel Flasher](https://github.com/fatalcoder524/KernelFlasher)
- [Releases](https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/releases)

---

## 💝 Donations

Any and all donations are appreciated!

- PayPal: [paypal.me/fatalcoder524](https://paypal.me/fatalcoder524)
- DM on Telegram for UPI donations!

## 🤝 Acknowledgments

- **[NoMount Suite](https://github.com/Bouteillepleine/NoMount-Suite)** &amp; all contributors — NoMount development 🙌 (built on **[maxsteeel/nomount](https://github.com/maxsteeel/nomount)**)
- **KernelSU Next** — the root solution
- **AnyKernel3** by osm0sis and contributors
- **[WildKernels/OnePlus_KernelSU_SUSFS](https://github.com/WildKernels/OnePlus_KernelSU_SUSFS)** — the excellent OnePlus build framework this is forked from
- **OnePlusOSS** — kernel source
- Community testers and contributors
---

## 📄 License

[GPL-2.0](LICENSE) — the same license as the Linux kernel this builds.

Kernel source comes from **OnePlusOSS** (GPL-2.0); the build framework is forked from
**[WildKernels/OnePlus_KernelSU_SUSFS](https://github.com/WildKernels/OnePlus_KernelSU_SUSFS)**.
The **NoMount Suite** add-on is a separate project — see [NoMount Suite](https://github.com/Bouteillepleine/NoMount-Suite) for its own license.
