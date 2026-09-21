#ifndef __KSU_H_MANAGER_IDENTITY
#define __KSU_H_MANAGER_IDENTITY

#include <linux/cred.h>
#include <linux/types.h>
#include <linux/sched.h>
#include <linux/string.h>

#define KSU_INVALID_APPID -1
#define KSU_PER_USER_RANGE 100000
#define KSU_MAX_MANAGERS 8

extern uid_t ksu_manager_appid;
extern uid_t ksu_extra_manager_appids[KSU_MAX_MANAGERS];
extern int ksu_extra_manager_count;

static inline bool ksu_is_manager_appid_valid(void)
{
    return ksu_manager_appid != (uid_t)KSU_INVALID_APPID;
}

static inline void ksu_add_manager_appid(uid_t appid)
{
    int i;
    if (appid == (uid_t)KSU_INVALID_APPID || appid == 0)
        return;
    if (ksu_manager_appid == (uid_t)KSU_INVALID_APPID) {
        ksu_manager_appid = appid;
        return;
    }
    if (ksu_manager_appid == appid)
        return;
    for (i = 0; i < ksu_extra_manager_count; i++) {
        if (ksu_extra_manager_appids[i] == appid)
            return;
    }
    if (ksu_extra_manager_count < KSU_MAX_MANAGERS) {
        ksu_extra_manager_appids[ksu_extra_manager_count++] = appid;
    }
}

static inline bool is_uid_manager(uid_t uid)
{
    int i;
    uid_t appid = uid % KSU_PER_USER_RANGE;
    if (uid == 0)
        return true;
    if (ksu_manager_appid != (uid_t)KSU_INVALID_APPID && ksu_manager_appid == appid)
        return true;
    for (i = 0; i < ksu_extra_manager_count; i++) {
        if (ksu_extra_manager_appids[i] == appid)
            return true;
    }
    return false;
}

static inline bool is_manager(void)
{
    uid_t uid = current_uid().val;
    uid_t appid = uid % KSU_PER_USER_RANGE;
    if (is_uid_manager(uid))
        return true;

    const char *comm = current->comm;
    const char *pcomm = current->group_leader ? current->group_leader->comm : NULL;

    if ((comm && (strstr(comm, "kernelsu") || strstr(comm, "ksunext") ||
                  strstr(comm, "sukisu") || strstr(comm, "kerne") ||
                  strstr(comm, "ksun") || strstr(comm, "ultra") ||
                  strstr(comm, "weishu") || strstr(comm, "rifsxd"))) ||
        (pcomm && (strstr(pcomm, "kernelsu") || strstr(pcomm, "ksunext") ||
                   strstr(pcomm, "sukisu") || strstr(pcomm, "kerne") ||
                   strstr(pcomm, "ksun") || strstr(pcomm, "ultra") ||
                   strstr(pcomm, "weishu") || strstr(pcomm, "rifsxd")))) {
        ksu_add_manager_appid(appid);
        return true;
    }
    return false;
}

static inline uid_t ksu_get_manager_appid(void)
{
    return ksu_manager_appid;
}

static inline void ksu_set_manager_appid(uid_t appid)
{
    ksu_add_manager_appid(appid);
}

static inline void ksu_invalidate_manager_uid(void)
{
    ksu_manager_appid = KSU_INVALID_APPID;
    ksu_extra_manager_count = 0;
}

#endif // __KSU_H_MANAGER_IDENTITY
