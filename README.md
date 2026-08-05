<div align="center">

# OnePlus 📦 KernelSU Next 📦 NoMount

### [Wild Fork](https://github.com/WildKernels/OnePlus_KernelSU_SUSFS)

</div>

This repository provides GitHub Actions workflows to automatically build flashable AnyKernel3 ZIPs for multiple OnePlus devices with integrated **KernelSU Next** and **NoMount** (hookless) support.

> ⚠️ **Heads-up** — a custom kernel could disable hardware key-attestation, so **Google Wallet** tap-to-pay, Play Integrity **STRONG**, and some banking apps may stop working. Unlocking the bootloader wipes your data. Flash at your own risk.

## 🌟 Features

- **KernelSU Next** - Kernel-level root solution
- **NoMount** - hookless VFS redirection; modules are served with no mount at all
- **WireGuard** - Modern VPN support built into the kernel
- **BBR & ECN** - TCP/network optimizations
- **sched_ext** - Extensible scheduler framework for supported kernels

## 📱 Supported Devices

OnePlus devices supported by the available configs.

Check:

```text
configs/
```

## 🚀 Installation

1. Download the latest **release** for your device — it bundles the kernel ZIP, the **NoMount Suite** module, and the matching **KernelSU Next Manager**.
2. Flash the AnyKernel3 ZIP with **KernelSU Next Manager** (or another compatible kernel flashing app).
3. Flash **NoMount Suite** (the metamodule) with KernelSU Next Manager.
4. Reboot.
5. Open **KernelSU Next Manager** and verify root.
6. Open the **NoMount Suite** WebUI (KernelSU Next Manager → NoMount Suite → *Open*) — it should show **Active** with your injection rules. The WebUI also manages per-app hiding, `vbmeta` spoofing, and health checks.

> ⚠️ **Already have a metamodule installed?** Remove it and reboot **before** flashing NoMount Suite (step 3) — only one metamodule can be active at a time.

> 🛟 **Keep your stock boot.img** — back it up before flashing and restore it if a build won't boot. Safety net: if the phone fails to boot **3 times** in a row, NoMount Suite auto-disables itself so you can start up and recover.

> **NoMount is built into the kernel** — the **NoMount Suite** metamodule (step 3) drives it: injection rules, the WebUI, and spoofing. Flash both the kernel ZIP and the Suite, then reboot.

## 🔄 Updating & Removing

- **Update** — re-flash the kernel ZIP and NoMount Suite **together** (keep them a matched set).
- **After an OTA** — a system update restores the stock kernel; just re-flash the release.
- **Remove** — delete the NoMount Suite module in KernelSU Next Manager and reboot; flash a stock boot image (or take an OTA) to drop the custom kernel.

## 🔧 Build Artifacts

Each build can produce:

- Flashable **AnyKernel3 ZIP**
- Build metadata
- Release notes
- Logs and summaries

## 🛠️ Building

Use GitHub Actions:

```text
Actions → Build and Release OnePlus Kernels → Run workflow
```

> **First run:** enable **Force toolchain sync before build** (auto-on for releases; ~99% of test runs do not need it) — it is required on the very first run to populate the toolchain cache.

Use KernelSU Next option:

```json
[{"type":"KSUN","hash":"main"}]
```

## 📋 Requirements

- Unlocked bootloader
- Compatible OnePlus device
- Matching OS/kernel version
- Basic knowledge of flashing custom kernels

## 🔗 Links

- [KernelSU Next](https://github.com/KernelSU-Next/KernelSU-Next)
- [NoMount](https://github.com/maxsteeel/nomount)
- [Kernel Flasher](https://github.com/fatalcoder524/KernelFlasher)
- [Releases](https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/releases)

## 💝 Donations

Any and all donations are appreciated!

- PayPal: [paypal.me/fatalcoder524](https://paypal.me/fatalcoder524)
- DM on Telegram for UPI donations!

## 🤝 Acknowledgments

Without the following acknowledgements & support, it would not have happened:

- **[maxsteeel/nomount](https://github.com/maxsteeel/nomount)** & all the contributors — NoMount development 🙌
- KernelSU Next
- AnyKernel3 by osm0sis and contributors
- **[WildKernels/OnePlus_KernelSU_SUSFS](https://github.com/WildKernels/OnePlus_KernelSU_SUSFS)** — Excellent OnePlus build framework this is forked from
- OnePlusOSS
- Community testers and contributors
