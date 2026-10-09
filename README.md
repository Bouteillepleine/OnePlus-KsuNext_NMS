<div align="center">

# OnePlus · KernelSU Next · NoMount

### A custom OnePlus kernel + a **mountless** hiding add-on

*Automated AnyKernel3 builds for dozens of OnePlus models, with `KernelSU Next` root and **NoMount** hookless VFS redirection baked in.*

[![Latest Release](https://img.shields.io/github/v/release/Bouteillepleine/OnePlus-KsuNext_NMS?style=for-the-badge&logo=github&label=Latest%20Release&color=6C4AB6)](https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/Bouteillepleine/OnePlus-KsuNext_NMS/total?style=for-the-badge&logo=icloud&logoColor=white&label=Downloads&color=2E8B57)](https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/releases)
[![Build](https://img.shields.io/github/actions/workflow/status/Bouteillepleine/OnePlus-KsuNext_NMS/build-kernel-release.yml?style=for-the-badge&logo=githubactions&logoColor=white&label=Build)](https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/actions)
[![Stars](https://img.shields.io/github/stars/Bouteillepleine/OnePlus-KsuNext_NMS?style=for-the-badge&logo=github&color=E3B341)](https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/stargazers)

**Based on [WildKernels/OnePlus_KernelSU_SUSFS](https://github.com/WildKernels/OnePlus_KernelSU_SUSFS)**

</div>

> [!WARNING]
> A custom kernel can disable hardware key-attestation, so **Google Wallet** tap-to-pay, Play Integrity **STRONG**, and some banking apps may stop working. Unlocking the bootloader **wipes your data**. Back up your stock `boot.img` first. Flash at your own risk.

---

## A kernel plus an add-on

Every release contains two things. Flash the kernel first, then add NoMount Suite on top.

|  | The kernel, built here | NoMount Suite, the add-on |
|---|---|---|
| **What it is** | AnyKernel3 ZIP (`AK3_<device>_…zip`) with `KernelSU Next` root and `CONFIG_NOMOUNT=y` compiled in | `00_NoMount-Module-vX.Y.Z.zip`, the metamodule that switches NoMount **on** |
| **Where it comes from** | This repo's GitHub Actions, one ZIP per device | The separate **[NoMount Suite](https://github.com/Bouteillepleine/NoMount-Suite)**, attached to each release as an add-on (sorted to the top of the Assets list) |
| **How you install it** | Flash with **Kernel Flasher** or **KernelSU Next Manager** | **KernelSU Next Manager → Modules → Install from storage** |
| **Get it now** | [⬇️ Latest release](https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/releases/latest) | [⬇️ Latest release](https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/releases/latest). It's at the top of the Assets list |

> [!IMPORTANT]
> **The kernel on its own does nothing visible.** NoMount is *compiled in* but stays **dormant** until the **NoMount Suite** module activates it. NoMount Suite is the part that carries your injection rules, the WebUI, and the spoofing. Think of it like a Magisk/KSU module. **You need both.**

## Optional: SUSFS

Every kernel ZIP also carries `susfs_guard_lkm.ko`, built against that exact kernel and
inert unless something loads it. Flashing the kernel drops it into `Download`; installing
`00_Loader-Module-vX.Y.zip` (also in the Assets) picks it up and loads it at every boot.

Skip it and nothing changes. One module per kernel: by design it will not load on a
build it was not compiled against.

---

## Why NoMount

Most hiding solutions mount something, an `overlayfs` or a bind mount, to swap files in.
Every mount is a line in `/proc/mounts` and an `st_dev` mismatch a detector can read.

NoMount serves your modules with no mounts at all. It's a hookless, per-inode VFS
redirection inside the kernel:

- **Nothing in the mount table.** No overlay, no bind mounts.
- **Per-app, per-file.** Redirect only the files you pick, only for the UIDs you pick.
- **Nothing to catch.** You can't be caught hiding a mount that never existed.
- **Driven from the WebUI.** Rules, per-app hiding and health checks, inside your manager.

<table>
  <tr>
    <td align="center"><a href="https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/blob/NoMount/docs/screenshots/status.jpg"><img src="https://raw.githubusercontent.com/Bouteillepleine/OnePlus-KsuNext_NMS/NoMount/docs/screenshots/status.jpg" width="155" alt="Status"></a></td>
    <td align="center"><a href="https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/blob/NoMount/docs/screenshots/hiding.jpg"><img src="https://raw.githubusercontent.com/Bouteillepleine/OnePlus-KsuNext_NMS/NoMount/docs/screenshots/hiding.jpg" width="155" alt="Hiding"></a></td>
    <td align="center"><a href="https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/blob/NoMount/docs/screenshots/rules.jpg"><img src="https://raw.githubusercontent.com/Bouteillepleine/OnePlus-KsuNext_NMS/NoMount/docs/screenshots/rules.jpg" width="155" alt="Rules"></a></td>
    <td align="center"><a href="https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/blob/NoMount/docs/screenshots/diagnostics.jpg"><img src="https://raw.githubusercontent.com/Bouteillepleine/OnePlus-KsuNext_NMS/NoMount/docs/screenshots/diagnostics.jpg" width="155" alt="Checks"></a></td>
    <td align="center"><a href="https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/blob/NoMount/docs/screenshots/duckdetector.jpg"><img src="https://raw.githubusercontent.com/Bouteillepleine/OnePlus-KsuNext_NMS/NoMount/docs/screenshots/duckdetector.jpg" width="155" alt="Duck Detector"></a></td>
  </tr>
  <tr>
    <td align="center"><sub><b>Status</b></sub></td>
    <td align="center"><sub><b>Hiding</b></sub></td>
    <td align="center"><sub><b>Rules</b></sub></td>
    <td align="center"><sub><b>Checks</b></sub></td>
    <td align="center"><sub><b>Duck Detector</b></sub></td>
  </tr>
</table>

<sub>Tap a screenshot to enlarge.</sub>

---

## What else is in the kernel

- **KernelSU Next**, kernel-level root.
- **WireGuard**, built into the kernel.
- **BBR and ECN** for TCP.
- **sched_ext**, the extensible scheduler framework, on kernels that carry it.

---

## Supported devices

One build fans out to dozens of OnePlus models, Android 13 to 16, kernel 5.10 to 6.12.
See the [**latest release**](https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/releases/latest) for the full, per-device list, or browse:

```text
configs/
```

---

## Installation

**Prerequisites:** unlocked bootloader · a backed-up stock `boot.img` · **[Kernel Flasher](https://github.com/fatalcoder524/KernelFlasher/releases)** installed.

1. **Download** the [latest release](https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/releases/latest) and grab **both**:
   - the **kernel** ZIP matching your exact device / OS / kernel base, and
   - the **`00_NoMount-Module-vX.Y.Z.zip`** add-on (top of the Assets list).
2. **Flash the kernel** ZIP with **Kernel Flasher** (or **KernelSU Next Manager**).
3. **Install the KernelSU Next Manager APK.** Use the version shown as `KernelSU Next Version` in the release notes.
4. **Add NoMount Suite:** KernelSU Next Manager → **Modules → Install from storage** → select `00_NoMount-Module-…zip`.
   > Already have a metamodule? Remove it and reboot **first**: only one metamodule can be active at a time.
5. **Reboot.**
6. Open **KernelSU Next Manager → NoMount Suite → Open**. The WebUI should show **Active** with your rules.

Safety net: three boots in a row that never finish and NoMount disables itself, so the
fourth comes up without it. Keep your stock `boot.img` handy either way.

---

## Updating and removing

- **Update** — re-flash the kernel ZIP **and** NoMount Suite together (keep them a matched set).
- **After an OTA** — the system update restores the stock kernel; just re-flash the release.
- **Remove** — delete NoMount Suite in KernelSU Next Manager and reboot, then flash a stock boot image (or take an OTA) to drop the custom kernel.

---

## FAQ

**Do I really need the module?** Yes. The kernel ships NoMount dormant and the Suite activates it. No Suite, no hiding.

**Where does the module come from?** It's a **separate add-on**, maintained in the [NoMount Suite](https://github.com/Bouteillepleine/NoMount-Suite) and attached to each release as `00_NoMount-Module-vX.Y.Z.zip` (named to sort to the top of the Assets).

**Can I keep my current kernel and just flash the module?** No. NoMount must be compiled into the kernel (`CONFIG_NOMOUNT=y`), so use the kernel from this release.

**Will it pass Play Integrity or my bank?** NoMount removes the mount signal. It cannot restore hardware key-attestation, which a custom kernel may break (STRONG, Wallet). Test with your own apps.

---

## Building it yourself

Via GitHub Actions:

```text
Actions → Build and Release OnePlus Kernels → Run workflow
```

Root option:

```json
[{"type":"KSUN","hash":"main"}]
```

> **First run:** enable **Force toolchain sync before build** (auto-on for releases). Required once to populate the toolchain cache.

---

## Links

- [KernelSU Next](https://github.com/KernelSU-Next/KernelSU-Next) · [KernelSU Next Manager releases](https://github.com/KernelSU-Next/KernelSU-Next/releases)
- [NoMount Suite](https://github.com/Bouteillepleine/NoMount-Suite) — the hiding add-on
- [Kernel Flasher](https://github.com/fatalcoder524/KernelFlasher)
- [Releases](https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/releases)

---

## Donations

Appreciated, never expected.

- PayPal: [paypal.me/fatalcoder524](https://paypal.me/fatalcoder524)
- DM on Telegram for UPI donations!

## Acknowledgments

- **[NoMount Suite](https://github.com/Bouteillepleine/NoMount-Suite)** &amp; all contributors — NoMount development 🙌 (built on **[maxsteeel/nomount](https://github.com/maxsteeel/nomount)**)
- **KernelSU Next** — the root solution
- **AnyKernel3** by osm0sis and contributors
- **[WildKernels/OnePlus_KernelSU_SUSFS](https://github.com/WildKernels/OnePlus_KernelSU_SUSFS)** — the excellent OnePlus build framework this is forked from
- **[inforcqb/susfs4ksu-lkm](https://github.com/inforcqb/susfs4ksu-lkm)** — SUSFS as a loadable module, which is what each kernel here carries
- **OnePlusOSS** — kernel source
- Community testers and contributors
---

## License

[GPL-2.0](LICENSE), the same license as the kernel this builds.

Kernel source comes from **OnePlusOSS** (GPL-2.0); the build framework is forked from
**[WildKernels/OnePlus_KernelSU_SUSFS](https://github.com/WildKernels/OnePlus_KernelSU_SUSFS)**.
The **NoMount Suite** add-on is a separate project; see [NoMount Suite](https://github.com/Bouteillepleine/NoMount-Suite) for its own license.
