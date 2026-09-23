# GKI 5.10 Kernel Builder

Universal 5.10 GKI kernel with APatch root support.

## Features

- Android Common Kernel 5.10.270 (Rama ACK)
- APatch root via KernelPatch binary patching
- TCP BBR congestion control with FQ scheduler
- Thin LTO optimization
- Pure stock Android kernel naming

## Output

- `Image` patched kernel
- `Image.gz` compressed patched kernel
- `Kernel-5.10.270-Universal.zip` AnyKernel3 flashable
- `APatch_11224.apk` manager

## Usage

Flash the AnyKernel3 zip via TWRP or custom recovery.
Install APatch manager after boot.

SuperKey: `apatch2026`

Enter the SuperKey in APatch manager when prompted to activate root.
