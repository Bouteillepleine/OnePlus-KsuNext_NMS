# OnePlus · KernelSU Next · NoMount · SUSFS

**[English](README.md)** | 简体中文

> 本页仅为简要说明。支持机型、内核功能、FAQ 与自行构建等完整内容，以 [英文 README](README.md) 为准。

为数十款一加机型自动构建的 AnyKernel3 内核，内置 KernelSU Next root、SUSFS，以及 **NoMount**（无挂载的 VFS 重定向隐藏）。

> [!WARNING]
> 自定义内核可能导致硬件密钥认证失效：Google Wallet 感应支付、Play Integrity **STRONG** 及部分银行应用可能无法使用。解锁 Bootloader 会**清除全部数据**。刷入前请备份原厂 `boot.img`，风险自负。

## 内核 + 附加模块

每个 Release 包含两部分，**缺一不可**：

- **内核**：`AK3_<机型>_….zip`，已编译 `CONFIG_NOMOUNT=y`。单独刷入时 NoMount 处于休眠状态，不会生效。
- **NoMount Suite**：`00_NoMount-Module-vX.Y.Z.zip`（位于 Assets 列表顶部），负责启用 NoMount，并提供规则、WebUI 与伪装功能。

## 安装

前提：已解锁 Bootloader、已备份原厂 `boot.img`、已安装 [Kernel Flasher](https://github.com/fatalcoder524/KernelFlasher/releases)。

1. 从 [最新 Release](https://github.com/Bouteillepleine/OnePlus-KsuNext_NMS/releases/latest) 下载与你的**机型 / 系统版本 / 内核版本完全对应**的内核 ZIP，以及 `00_NoMount-Module-…zip`。
2. 用 **Kernel Flasher**（或 KernelSU Next 管理器）刷入内核 ZIP。
3. 安装 Release 中附带的 KernelSU Next 管理器 APK（普通版或 spoofed 版，二选一）。请使用附带的版本：管理器与内核驱动必须来自同一构建，否则无法通信。
4. KernelSU Next 管理器 → **模块 → 从本地安装** → 选择 `00_NoMount-Module-…zip`。如已安装其他元模块（metamodule），请先删除并重启：同一时间只能启用一个。
5. 重启后打开 KernelSU Next 管理器 → NoMount Suite → 打开，WebUI 应显示 **Active**。

连续三次启动未完成时，NoMount 会自动停用，第四次启动将不再加载它。

## 更新与卸载

- **更新**：内核 ZIP 与 NoMount Suite 请一起重新刷入，保持版本配套。
- **系统 OTA** 会还原原厂内核，OTA 完成后重新刷入即可。
- **卸载**：在 KernelSU Next 管理器 中删除 NoMount Suite 并重启，再刷回原厂 boot 镜像（或进行一次 OTA）。
