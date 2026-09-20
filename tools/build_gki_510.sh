#!/bin/bash
# ==============================================================================
# Rama982 GKI 5.10 + KernelSU Kernel Build Script
# Matches Rama's exact production build configuration
# ==============================================================================
set -euo pipefail

# --- Configuration ---------------------------------------------------------
readonly LLVM_VERSION="23.1.0-rc3"
readonly LLVM_ARCH="x86_64"
readonly LLVM_MAJOR="${LLVM_VERSION%%.*}"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly KERNEL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
readonly TOOLCHAIN_ROOT="$KERNEL_ROOT/tools/toolchain"
readonly CLANG_URL="https://mirrors.edge.kernel.org/pub/tools/llvm/files/llvm-${LLVM_VERSION}-${LLVM_ARCH}.tar.xz"
readonly CLANG_HOME="$TOOLCHAIN_ROOT/clang-${LLVM_MAJOR}"
readonly SRCDIR="$KERNEL_ROOT/sources/android_kernel_common-5.10"
readonly OUT_DIR="$SRCDIR/out"
readonly ANYKERNEL_DIR="$KERNEL_ROOT/tools/AnyKernel3"
readonly BUILDS_DIR="$KERNEL_ROOT/builds"
readonly TARGET_ARCH="arm64"
readonly LOCAL_VERSION="-Rama982-RE/r26-KSU"
readonly TIMEZONE="Asia/Jakarta"

# --- Logging ---------------------------------------------------------------
log_info() { printf '\033[0;32m[INFO]\033[0m %s\n' "$1"; }
log_warn() { printf '\033[1;33m[WARN]\033[0m %s\n' "$1"; }
log_err()  { printf '\033[0;31m[ERROR]\033[0m %s\n' "$1" >&2; }

# --- Toolchain Fetching ----------------------------------------------------
fetch_toolchain() {
    local n=$1 u=$2 d=$3 m=$4
    [[ -n "$m" && -e "$d/$m" ]] && { log_info "Toolchain $n already prepared."; return 0; }

    log_info "Downloading toolchain $n ($u)..."
    mkdir -p "$d"

    local t; t=$(mktemp) || { log_err "Failed to create temp file."; return 1; }

    local -a cmd
    if   command -v curl >/dev/null; then cmd=(curl -fL "$u" -o "$t")
    elif command -v wget >/dev/null; then cmd=(wget -qO "$t" "$u")
    else rm -f "$t"; log_err "Neither curl nor wget found."; return 1; fi

    if ! "${cmd[@]}"; then
        rm -f "$t"; log_err "Failed to download toolchain from $u."; return 1
    fi
    log_info "Extracting toolchain to $d..."
    if ! tar -xJf "$t" -C "$d" --strip-components=1; then
        rm -f "$t"; log_err "Failed to extract toolchain."; return 1
    fi
    rm -f "$t"
}

# --- Build Steps -----------------------------------------------------------
setup_environment() {
    export PATH="$CLANG_HOME/bin:$PATH" LLVM=1 LLVM_IAS=1 \
           ARCH="$TARGET_ARCH" LOCALVERSION="$LOCAL_VERSION" LTO=thin \
           TZ="$TIMEZONE"
}

configure_kernel() {
    log_info "Configuring kernel with gki_defconfig + KernelSU..."
    cd "$SRCDIR"
    mkdir -p "$OUT_DIR"
    printf '%s' "-g$(git rev-parse --short HEAD 2>/dev/null || true)" > .scmversion
    
    make O="$OUT_DIR" ARCH="$TARGET_ARCH" gki_defconfig
    
    # Enable LTO and KernelSU flags
    scripts/config --file "$OUT_DIR/.config" \
        -e LTO_CLANG -e LTO_CLANG_THIN -d LTO_NONE -d LTO_CLANG_FULL \
        -e KSU -e OVERLAY_FS -e KPROBES -e HAVE_KPROBES -e KPROBE_EVENTS
        
    make O="$OUT_DIR" ARCH="$TARGET_ARCH" olddefconfig savedefconfig
}

build_kernel() {
    log_info "Building kernel Image using $(nproc --all) CPU threads..."
    cd "$SRCDIR"
    make -j"$(nproc --all)" O="$OUT_DIR" ARCH="$TARGET_ARCH" Image
}

package_anykernel() {
    local img="$OUT_DIR/arch/arm64/boot/Image"
    if [[ ! -f "$img" ]]; then
        log_err "Kernel image not found at $img! Build failed."
        exit 1
    fi
    
    log_info "Kernel built successfully! Packaging AnyKernel3 zip..."
    mkdir -p "$BUILDS_DIR"
    cp -v "$img" "$ANYKERNEL_DIR/Image"
    
    local date_tag
    date_tag=$(date +%Y%m%d-%H%M)
    local zip_name="AK3-Rama982-RE-r26-5.10-KSU-${date_tag}.zip"
    local final_zip="$BUILDS_DIR/$zip_name"
    
    cd "$ANYKERNEL_DIR"
    zip -r9 "$final_zip" ./* -x ".git*" "README.md" "*.zip"
    
    log_info "Flashable ZIP created: $final_zip"
}

# --- Main ------------------------------------------------------------------
main() {
    local t0=$SECONDS
    log_info "=== Starting Rama982 GKI 5.10 + KernelSU Build ==="
    
    fetch_toolchain "clang-$LLVM_MAJOR" "$CLANG_URL" "$CLANG_HOME" bin/clang
    setup_environment
    configure_kernel
    build_kernel
    package_anykernel

    log_info "All done in $(((SECONDS-t0)/60))m $(((SECONDS-t0)%60))s!"
}

main "$@"
