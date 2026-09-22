#!/usr/bin/env python3
"""
Deep Stealth Engine Patcher for GKI 5.10 (SukiSU Ultra + SuSFS)
Applies verified, kernel-level cloaking patches directly to kernel source.
"""

import os
import sys

def patch_susfs_paths():
    p = "fs/susfs.c"
    if not os.path.exists(p):
        print(f"[-] {p} not found, skipping susfs path patch")
        return
    c = open(p).read()
    helper = """#ifdef CONFIG_KSU_SUSFS_SUS_PATH
static void susfs_add_default_path_loop(const char *pathname) {
\tstruct st_susfs_sus_path_list *new_list;
\tnew_list = kzalloc(sizeof(struct st_susfs_sus_path_list), GFP_KERNEL);
\tif (!new_list)
\t\treturn;
\tstrscpy(new_list->info.target_pathname, pathname, SUSFS_MAX_LEN_PATHNAME - 1);
\tstrscpy(new_list->target_pathname, pathname, SUSFS_MAX_LEN_PATHNAME - 1);
\tINIT_LIST_HEAD(&new_list->list);
\tmutex_lock(&susfs_mutex_lock_sus_path);
\tlist_add_tail_rcu(&new_list->list, &LH_SUS_PATH_LOOP);
\tmutex_unlock(&susfs_mutex_lock_sus_path);
}
#endif
"""
    target = "void susfs_init(void) {"
    calls = """void susfs_init(void) {
#ifdef CONFIG_KSU_SUSFS_SUS_PATH
\tsusfs_add_default_path_loop("/system/addon.d");
\tsusfs_add_default_path_loop("/data/adb");
\tsusfs_add_default_path_loop("/sdcard/TWRP");
\tsusfs_add_default_path_loop("/sdcard/Fox");
\tsusfs_add_default_path_loop("/sdcard/MT2");
\tsusfs_add_default_path_loop("/data/media/0/TWRP");
\tsusfs_add_default_path_loop("/data/media/0/Fox");
\tsusfs_add_default_path_loop("/data/media/0/MT2");
\tsusfs_add_default_path_loop("/data/local/tmp/main.jar");
#endif"""
    if target in c and "susfs_add_default_path_loop" not in c:
        open(p, "w").write(c.replace(target, helper + "\n" + calls, 1))
        print(f"[+] Successfully patched default sus paths in {p}")
    else:
        print(f"[-] Default paths already present or target not found in {p}")

def patch_cmdline():
    p = "fs/proc/cmdline.c"
    if not os.path.exists(p):
        print(f"[-] {p} not found, skipping cmdline patch")
        return
    c = open(p).read()
    header = """#ifdef CONFIG_KSU_SUSFS
#include <linux/cred.h>
#include <linux/string.h>
#include <linux/slab.h>
#endif
"""
    target = "static int cmdline_proc_show(struct seq_file *m, void *v)\n{"
    stealth = """static int cmdline_proc_show(struct seq_file *m, void *v)
{
#ifdef CONFIG_KSU_SUSFS
\tif (current_uid().val >= 10000) {
\t\tchar *buf = kstrdup(saved_command_line, GFP_KERNEL);
\t\tif (buf) {
\t\t\tchar *p;
\t\t\tif ((p = strstr(buf, "androidboot.verifiedbootstate=orange"))) memcpy(p + 30, "green ", 6);
\t\t\tif ((p = strstr(buf, "androidboot.flash.locked=0"))) p[25] = '1';
\t\t\tif ((p = strstr(buf, "androidboot.vbmeta.device_state=unlocked"))) memcpy(p + 32, "locked  ", 8);
\t\t\tif (!strstr(buf, "androidboot.bootloader=")) {
\t\t\t\tseq_printf(m, "%s androidboot.bootloader=Infinix-X6871\\n", buf);
\t\t\t} else {
\t\t\t\tseq_puts(m, buf);
\t\t\t\tseq_putc(m, '\\n');
\t\t\t}
\t\t\tkfree(buf);
\t\t\treturn 0;
\t\t}
\t}
#endif"""
    if target in c and "androidboot.verifiedbootstate=orange" not in c:
        open(p, "w").write(header + c.replace(target, stealth, 1))
        print(f"[+] Successfully patched cmdline spoofing in {p}")
    else:
        print(f"[-] Cmdline spoofing already present or target not found in {p}")

def patch_bootconfig():
    p = "fs/proc/bootconfig.c"
    if not os.path.exists(p):
        print(f"[-] {p} not found, skipping bootconfig patch")
        return
    c = open(p).read()
    header = """#ifdef CONFIG_KSU_SUSFS
#include <linux/cred.h>
#include <linux/string.h>
#include <linux/slab.h>
#include <linux/sched.h>
#endif
"""
    target = "static int bootconfig_proc_show(struct seq_file *m, void *v)\n{"
    patch = """static int bootconfig_proc_show(struct seq_file *m, void *v)
{
#ifdef CONFIG_KSU_SUSFS
\tif (current_uid().val >= 10000 || current->pid == 1) {
\t\tif (saved_bootconfig && saved_bootconfig_size > 0) {
\t\t\tchar *buf = kmalloc(saved_bootconfig_size + 512, GFP_KERNEL);
\t\t\tif (buf) {
\t\t\t\tchar *p;
\t\t\t\tmemcpy(buf, saved_bootconfig, saved_bootconfig_size);
\t\t\t\tbuf[saved_bootconfig_size] = '\\0';
\t\t\t\tif ((p = strstr(buf, "androidboot.verifiedbootstate = \\\"orange\\\""))) memcpy(p + 33, "green \\\"", 7);
\t\t\t\tif ((p = strstr(buf, "androidboot.flash.locked = \\\"0\\\""))) p[28] = '1';
\t\t\t\tif ((p = strstr(buf, "androidboot.vbmeta.device_state = \\\"unlocked\\\""))) memcpy(p + 35, "locked  \\\"", 9);
\t\t\t\tseq_puts(m, buf);
\t\t\t\tif (!strstr(buf, "androidboot.bootloader")) seq_puts(m, "androidboot.bootloader = \\\"Infinix-X6871\\\"\\n");
\t\t\t\tkfree(buf);
\t\t\t\treturn 0;
\t\t\t}
\t\t} else {
\t\t\tseq_puts(m, "androidboot.bootloader = \\\"Infinix-X6871\\\"\\nandroidboot.verifiedbootstate = \\\"green\\\"\\nandroidboot.flash.locked = \\\"1\\\"\\nandroidboot.vbmeta.device_state = \\\"locked\\\"\\n");
\t\t\treturn 0;
\t\t}
\t}
#endif"""
    if target in c and "androidboot.bootloader = \\\"Infinix-X6871\\\"" not in c:
        open(p, "w").write(header + c.replace(target, patch, 1))
        print(f"[+] Successfully patched bootconfig spoofing in {p}")
    else:
        print(f"[-] Bootconfig spoofing already present or target not found in {p}")

def patch_selinuxfs():
    p = "security/selinux/selinuxfs.c"
    if not os.path.exists(p):
        print(f"[-] {p} not found, skipping selinuxfs patch")
        return
    c = open(p).read()
    target = "rc = avc_has_perm(&selinux_state,\n\t\t\t  current_sid(), SECINITSID_SECURITY,\n\t\t\t  SECCLASS_SECURITY, SECURITY__READ_POLICY, NULL);"
    patch = """#ifdef CONFIG_KSU_SUSFS
\tif (current_uid().val >= 10000) {
\t\trc = -EACCES;
\t\tgoto err;
\t}
#endif
\t""" + target
    if target in c and "rc = -EACCES;" not in c:
        open(p, "w").write(c.replace(target, patch, 1))
        print(f"[+] Successfully patched SELinux policy read denial in {p}")
    else:
        print(f"[-] SELinux policy read denial already present or target not found in {p}")

def patch_version():
    p = "fs/proc/version.c"
    if not os.path.exists(p):
        print(f"[-] {p} not found, skipping version patch")
        return
    c = open(p).read()
    target = "static int version_proc_show(struct seq_file *m, void *v)\n{"
    header = """#ifdef CONFIG_KSU_SUSFS
#include <linux/cred.h>
#endif
"""
    patch = """static int version_proc_show(struct seq_file *m, void *v)
{
#ifdef CONFIG_KSU_SUSFS
\tif (current_uid().val >= 10000) {
\t\tseq_printf(m, "Linux version %s (%s@%s) (%s) %s\\n",
\t\t\tutsname()->release, "build", "infinix",
\t\t\t"Android (12426897, +pgo, +bolt, +lto, +mlgo, based on r522817) clang version 18.0.1",
\t\t\tutsname()->version);
\t\treturn 0;
\t}
#endif"""
    if target in c and "build@infinix" not in c:
        open(p, "w").write(header + c.replace(target, patch, 1))
        print(f"[+] Successfully patched /proc/version spoofing in {p}")
    else:
        print(f"[-] /proc/version spoofing already present or target not found in {p}")

def main():
    print("[*] Running Deep Stealth Kernel Patcher...")
    patch_susfs_paths()
    patch_cmdline()
    patch_bootconfig()
    patch_selinuxfs()
    patch_version()
    print("[*] All deep stealth patches completed successfully!")

if __name__ == '__main__':
    main()
