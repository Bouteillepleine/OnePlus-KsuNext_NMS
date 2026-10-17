# Stock kernel configs

What `/proc/config.gz` reports when `stock_config` is set for a device, instead of
the real build config. The kernel still compiles from the real `.config`, so every
feature stays built in and working — only the IKCONFIG blob changes.

Lookup order, per build:

1. `<MODEL>.config` — an exact capture from that model's stock kernel.
2. `<android_version>-<kernel_version>.config` — family fallback, e.g. `android16-6.12.config`.
3. The official AOSP GKI prebuilt kernel for that kernel version, config read out of
   the image. Right for a GKI target, wrong for a vendor tree — which is why
   `stock_config` is opt-in per device config.

Capture one from a device running the stock kernel:

```
adb shell su -c 'zcat /proc/config.gz' > OP15-6.12.58.config
```

Keep the capture's kernel version aligned with what that config builds: a config
headed `6.12.23` under a `6.12.58` banner is a tell of its own. The build rewrites
the header line to match, but the rest of the config is whatever was captured.

| File | Source |
| --- | --- |
| `OP15-6.12.58.config` | OP15 CPH2747 Global, OOS 16.0.10.601, `6.12.58-android16-6` |
| `OP15-6.12.69.config` | OP15 PLK110 CN, 17.0.0.105, `6.12.69-android16-6` |
