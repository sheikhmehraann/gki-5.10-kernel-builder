import os
import re
import urllib.request

KPM_BASE = "https://raw.githubusercontent.com/SukiSU-Ultra/SukiSU-Ultra/builtin/kernel/kpm"
KPM_FILES = [
    "compact.c",
    "compact.h",
    "kpm.c",
    "kpm.h",
    "super_access.c",
    "super_access.h",
]

def setup_kpm(kernel_su_dir):
    kpm_dir = os.path.join(kernel_su_dir, "kernel", "kpm")
    os.makedirs(kpm_dir, exist_ok=True)

    for f in KPM_FILES:
        url = f"{KPM_BASE}/{f}"
        dest = os.path.join(kpm_dir, f)
        data = urllib.request.urlopen(url).read().decode("utf-8", errors="ignore")
        with open(dest, "w", encoding="utf-8") as fp:
            fp.write(data)

    # 1. Update kpm.h with struct ksu_kpm_cmd
    kpm_h_path = os.path.join(kpm_dir, "kpm.h")
    with open(kpm_h_path, "w", encoding="utf-8") as fp:
        fp.write("""#ifndef __SUKISU_KPM_H
#define __SUKISU_KPM_H

#include <linux/types.h>

struct ksu_kpm_cmd {
    __aligned_u64 __user control_code;
    __aligned_u64 __user arg1;
    __aligned_u64 __user arg2;
    __aligned_u64 __user result_code;
};

int sukisu_handle_kpm(unsigned long control_code, unsigned long arg3,
                      unsigned long arg4, unsigned long result_code);
int sukisu_is_kpm_control_code(unsigned long control_code);
int do_kpm(void __user *arg);

#define CMD_KPM_CONTROL 1
#define CMD_KPM_CONTROL_MAX 10

#endif
""")

    # 2. Fix super_access.c mount.h include
    sa_path = os.path.join(kpm_dir, "super_access.c")
    with open(sa_path, "r", encoding="utf-8") as fp:
        sa_content = fp.read()
    sa_content = sa_content.replace(
        "#include <../fs/mount.h>",
        """#if __has_include("../fs/mount.h")
#include "../fs/mount.h"
#elif __has_include("fs/mount.h")
#include "fs/mount.h"
#elif __has_include("../../fs/mount.h")
#include "../../fs/mount.h"
#endif"""
    )
    with open(sa_path, "w", encoding="utf-8") as fp:
        fp.write(sa_content)

    # 3. Add Kconfig entry for KPM
    kconfig_path = os.path.join(kernel_su_dir, "kernel", "Kconfig")
    with open(kconfig_path, "r", encoding="utf-8") as fp:
        kconfig = fp.read()
    if "config KPM" not in kconfig:
        kconfig = kconfig.replace(
            "endmenu",
            """config KPM
\tbool "Kernel Patch Module (KPM) support"
\tdepends on KSU && 64BIT
\tdefault y
\thelp
\t  Enable Kernel Patch Module (KPM) support.
\tselect KALLSYMS
\tselect KALLSYMS_ALL

endmenu"""
        )
        with open(kconfig_path, "w", encoding="utf-8") as fp:
            fp.write(kconfig)

    # 4. Include KPM into core/init.c
    init_path = os.path.join(kernel_su_dir, "kernel", "core", "init.c")
    with open(init_path, "r", encoding="utf-8") as fp:
        init_content = fp.read()
    if "CONFIG_KPM" not in init_content:
        init_content += """
#ifdef CONFIG_KPM
#include "../manager/manager_identity.h"
#include "../kpm/kpm.h"
#include "../kpm/compact.h"
#include "../kpm/super_access.h"
#include "../kpm/compact.c"
#include "../kpm/super_access.c"
#include "../kpm/kpm.c"
#endif
"""
        with open(init_path, "w", encoding="utf-8") as fp:
            fp.write(init_content)

    # 5. Patch dispatch.c: set LKM flag and add KPM supercall handlers
    dispatch_path = os.path.join(kernel_su_dir, "kernel", "supercall", "dispatch.c")
    with open(dispatch_path, "r", encoding="utf-8") as fp:
        dispatch = fp.read()

    # Always set LKM flag to clear GKI test environment warning
    dispatch = re.sub(r'(\.flags = 0 };)', r'\1\n    cmd.flags |= KSU_GET_INFO_FLAG_LKM;', dispatch)

    # Add KPM ioctl commands and handlers
    kpm_handlers = """
#ifdef CONFIG_KPM
#include "../kpm/kpm.h"
#define KSU_IOCTL_ENABLE_KPM _IOC(_IOC_READ, 'K', 102, 0)
#define KSU_IOCTL_KPM _IOC(_IOC_READ | _IOC_WRITE, 'K', 200, 0)

struct ksu_enable_kpm_cmd {
    __u8 enabled;
};

static int do_enable_kpm(void __user *arg)
{
    struct ksu_enable_kpm_cmd cmd = { .enabled = 1 };
    if (copy_to_user(arg, &cmd, sizeof(cmd)))
        return -EFAULT;
    return 0;
}
#endif
"""
    if "KSU_IOCTL_ENABLE_KPM" not in dispatch:
        dispatch = kpm_handlers + dispatch

        # Add to ksu_ioctl_handlers table
        table_entry = """#ifdef CONFIG_KPM
    {
        .cmd = KSU_IOCTL_ENABLE_KPM,
        .name = "GET_ENABLE_KPM",
        .handler = do_enable_kpm,
        .perm_check = manager_or_root
    },
    {
        .cmd = KSU_IOCTL_KPM,
        .name = "KPM_OPERATION",
        .handler = do_kpm,
        .perm_check = manager_or_root
    },
#endif
    { 
        .cmd = KSU_IOCTL_GRANT_ROOT,"""
        if "{ \n        .cmd = KSU_IOCTL_GRANT_ROOT," in dispatch:
            dispatch = dispatch.replace('{ \n        .cmd = KSU_IOCTL_GRANT_ROOT,', table_entry)
        else:
            dispatch = dispatch.replace('{\n        .cmd = KSU_IOCTL_GRANT_ROOT,', table_entry)

    with open(dispatch_path, "w", encoding="utf-8") as fp:
        fp.write(dispatch)

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "KernelSU"
    setup_kpm(target)
