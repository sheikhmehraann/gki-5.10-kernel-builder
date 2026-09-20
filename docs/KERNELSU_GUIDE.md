# KernelSU Integration & Rama982 Kernel Guide

This workspace is configured for kernel development, modding, and KernelSU integration for **Rama982** kernels and GKI/MediaTek trees.

---

## 1. Directory Structure

```text
C:\Users\Admin\Videos\Github\Kernel\
├── builds/                 # Flashable zip releases & prebuilt kernels
│   └── AK3-Rama982-RE-r24-5.10.261-noSU.zip
├── sources/                # Kernel source trees
│   ├── android_kernel_common-5.10/  (Rama982 GKI 5.10 DAMON)
│   ├── android_kernel_alps-5.10/    (MediaTek ALPS MT6789 / G99)
│   └── ...
├── tools/                  # Packaging and build utilities
│   ├── AnyKernel3/         # AnyKernel3 template for creating flashable zips
│   ├── KernelSU/           # Official KernelSU repository & driver source
│   ├── dokar/              # Dockerfile build environment for kernel compilation
│   ├── kernel_manifest/    # Repo manifest for syncing kernel common & toolchain
│   ├── kernel_devicetree/  # Xiaomi device trees
│   └── sync_rama_kernels.ps1 # Automation script to clone/sync Rama repos
└── docs/                   # Guides, references, and defconfig notes
    └── KERNELSU_GUIDE.md
```

---

## 2. KernelSU Integration in GKI 5.10 (Rama982)

KernelSU operates in kernel space and requires:
- `CONFIG_KSU=y`
- `CONFIG_OVERLAY_FS=y`
- `CONFIG_KPROBES=y`
- `CONFIG_HAVE_KPROBES=y`
- `CONFIG_KPROBE_EVENTS=y`

### Method A: Automated Setup Script (Linux / WSL / Docker)
Run inside the kernel source root:
```bash
curl -LSs "https://raw.githubusercontent.com/tiann/KernelSU/main/kernel/setup.sh" | bash -
```
For the latest development branch:
```bash
curl -LSs "https://raw.githubusercontent.com/tiann/KernelSU/main/kernel/setup.sh" | bash -s main
```

### Method B: Git Submodule / Local Integration
1. Link or copy `tools/KernelSU/kernel` into `drivers/kernelsu`:
```bash
ln -s ../../tools/KernelSU/kernel drivers/kernelsu
```
2. In `drivers/Makefile`, append:
```make
obj-y += kernelsu/
```
3. In `drivers/Kconfig`, add:
```kconfig
source "drivers/kernelsu/Kconfig"
```
4. Enable configs in `arch/arm64/configs/gki_defconfig`:
```properties
CONFIG_KSU=y
CONFIG_OVERLAY_FS=y
CONFIG_KPROBES=y
CONFIG_HAVE_KPROBES=y
CONFIG_KPROBE_EVENTS=y
```

---

## 3. AnyKernel3 Packaging (Creating Flashable Zips)

When compiling a kernel (produces `arch/arm64/boot/Image`), you can package it into a flashable zip using `tools/AnyKernel3`:

1. Copy the compiled `Image` to `tools/AnyKernel3/Image`:
   ```bash
   cp arch/arm64/boot/Image tools/AnyKernel3/Image
   ```
2. Verify `anykernel.sh` configuration:
   - `kernel.string=GKI 5.10 Rama982 RE by ramabondanp`
   - `do.devicecheck=0`
   - `is_slot_device=1`
3. Zip the contents:
   ```bash
   cd tools/AnyKernel3
   zip -r9 ../../builds/AK3-Rama982-RE-r24-5.10.261-KSU.zip * -x .git .github README.md
   ```

---

## 4. Key Links & References
- **Rama982 GitHub Profile:** [ramabondanp](https://github.com/ramabondanp)
- **SourceForge KERNEL Directory:** [rama982 KERNEL Files](https://sourceforge.net/projects/rama982/files/KERNEL/)
- **KernelSU Official Documentation:** [kernelsu.org](https://kernelsu.org/)
- **KernelSU GitHub Repository:** [tiann/KernelSU](https://github.com/tiann/KernelSU)
