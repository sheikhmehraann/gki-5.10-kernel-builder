### AnyKernel3 Ramdisk Mod Script
## osm0sis @ xda-developers

### AnyKernel setup
# Global properties
properties() { '
kernel.string=Kernel By Mehraan (VARIANT)
do.devicecheck=0
do.modules=0
do.systemless=1
do.cleanup=1
do.cleanuponabort=0
device.name1=
supported.versions=5.10 - 5.10.271
supported.patchlevels=
'; } # end properties

### AnyKernel install

## Boot shell variables
BLOCK=boot;
IS_SLOT_DEVICE=auto;
RAMDISK_COMPRESSION=auto;
PATCH_VBMETA_FLAG=auto;

# Import functions/variables and setup patching - see for reference (DO NOT REMOVE)
. tools/ak3-core.sh;

## Start boot install
split_boot;
flash_boot;
## End boot install
