# GKI 5.10 Kernel Builder

Automated builder for Android Common Kernel 5.10 GKI with KernelSU and KPM support.

## Overview

- Kernel: Android Common Kernel 5.10 (android12-5.10-stg-damon, sublevel 270)
- Root: KernelSU latest (v3.3.0)
- Kernel Patch Module (KPM): enabled
- Toolchain: LLVM 17.0.6 (Kernel.org)
- Packaging: AnyKernel3 universal flashable zip

## Build Configuration

- CONFIG_KSU=y
- CONFIG_KPM=y
- CONFIG_KALLSYMS=y
- CONFIG_KALLSYMS_ALL=y
- CONFIG_KPROBES=y
- CONFIG_LTO_CLANG_THIN=y

Kernel localversion is set to `-android12-9-00014-gf82f7360927e-ab14119954` with `android-build` build user and host to match stock Android release builds.

## Output Artifacts

- Image: raw uncompressed kernel image
- Image.gz: gzip-compressed kernel image
- KernelSU-5.10.270-Universal.zip: AnyKernel3 recovery flashable package
- KernelSU_v3.3.0.apk: official manager application
