# Android Kernel Workspace — Rama982 & KernelSU

Welcome to the organized workspace for **Android Kernel Development**, focusing on **Rama982** kernels and **KernelSU** integration.

---

## 📁 Workspace Directory Structure

```text
C:\Users\Admin\Videos\Github\Kernel\
├── builds\                         # Flashable packages & prebuilt releases
│   └── AK3-Rama982-RE-r24-5.10.261-noSU.zip
│
├── sources\                        # Cloned kernel source trees
│   ├── android_kernel_common-5.10\ # Rama982 GKI 5.10 kernel tree (DAMON branch)
│   ├── android_kernel_alps-5.10\   # MediaTek ALPS 5.10 kernel (MT6789 / Helio G99)
│   └── ...                         # Other device/common kernel sources
│
├── tools\                          # Utilities, manifests, and build helpers
│   ├── AnyKernel3\                 # Rama's AnyKernel3 flashable packaging template
│   ├── KernelSU\                   # Official KernelSU repository & driver source
│   ├── dokar\                      # Docker environment for compiling Android kernels
│   ├── kernel_manifest\            # Repo manifest for AOSP / Rama kernel builds
│   ├── kernel_devicetree\          # Kernel devicetree projects
│   └── sync_rama_kernels.ps1       # Automated clone/sync script for Rama's repos
│
└── docs\                           # Documentation & guides
    └── KERNELSU_GUIDE.md           # Step-by-step KernelSU integration guide
```

---

## 🛠️ Rama982 Kernel Ecosystem

- **Developer:** Rama Bondan Prakoso ([@ramabondanp](https://github.com/ramabondanp) / [@rama982](https://github.com/rama982))
- **Kernel Series:** Rama982 RE (Generic Kernel Image 5.10 & MediaTek platforms)
- **SourceForge Releases:** [rama982 KERNEL Downloads](https://sourceforge.net/projects/rama982/files/KERNEL/)
- **Features:**
  - Android Generic Kernel Image (GKI) 5.10 up to 5.10.261+
  - DAMON (Data Access Monitor) memory reclaim optimizations
  - GPU Overclocking (GPUOC) for MT6789 (Helio G99)
  - AnyKernel3 flashable zips supporting dynamic partitions and slot A/B devices

---

## ⚡ KernelSU Integration

- **Official Website:** [kernelsu.org](https://kernelsu.org/)
- **Official Repository:** [tiann/KernelSU](https://github.com/tiann/KernelSU)

### Required Kernel Configs:
```ini
CONFIG_KSU=y
CONFIG_OVERLAY_FS=y
CONFIG_KPROBES=y
CONFIG_HAVE_KPROBES=y
CONFIG_KPROBE_EVENTS=y
```

For full manual and automatic integration instructions, consult [`docs/KERNELSU_GUIDE.md`](docs/KERNELSU_GUIDE.md).

---

## 🔄 Automated Repository Management

To clone or update additional kernel source trees from Rama's GitHub profile, run:

```powershell
pwsh tools/sync_rama_kernels.ps1
```
