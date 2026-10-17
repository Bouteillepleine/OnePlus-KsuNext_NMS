# Stock kernel configs

What `/proc/config.gz` reports when `stock_config` is set for a device, instead of
the real build config. The kernel still compiles from the real `.config`, so every
feature stays built in and working — only the IKCONFIG blob changes.

Source order, per build:

1. `<MODEL>.config` — an exact capture from that model's stock kernel. Authoritative:
   it is what the device actually shipped.
2. `<android_version>-<kernel_version>.config` — family fallback, e.g. `android16-6.12.config`.
3. **A snapshot resolved from the model's own kernel source**, taken before any of our
   patches touch `gki_defconfig` (`make gki_defconfig olddefconfig` on the pristine
   tree). This covers every model with no capture, carries the vendor and SoC symbols
   an AOSP GKI config would not have, and tracks the sublevel being built — so it
   cannot go stale. This is why only genuine captures live in this directory.
4. The official AOSP GKI prebuilt kernel for that kernel version, config read out of
   the image. Last resort, used only if the defconfig resolve failed.

The snapshot is copied to the debug artifacts as `stock_config_<MODEL>.config`, and its
line count and sha256 are printed in the build log, so what a build serves is auditable
without committing it.

Capture one from a device running the stock kernel:

```
adb shell su -c 'zcat /proc/config.gz' > OP15-6.12.58.config
```

A capture is pinned to one sublevel. The build rewrites the header line to the kernel
being built, but the body stays whatever was captured — so refresh a capture when that
model's stock kernel moves, or delete it and let the snapshot handle it.

| File | Source |
| --- | --- |
| `OP15-6.12.58.config` | OP15 CPH2747 Global, OOS 16.0.10.601, `6.12.58-android16-6` |
| `OP15-6.12.69.config` | OP15 PLK110 CN, 17.0.0.105, `6.12.69-android16-6` |
