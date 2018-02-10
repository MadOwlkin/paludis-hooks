def hook_run_sync_all_post(env, hook_env):
    import os
    import shutil

    ret = 0
    key_location = "/var/lib/gentoo/gkeys/keyrings/gentoo/release/pubring.gpg"
    portage_tree = "/usr/portage"
    gemato_cmd = "gemato verify %s -K %s -s" % (portage_tree, key_location)
    targets = hook_env["TARGETS"].split(" ")
    for name in targets:
        if name == "gentoo":
            print "Verifying integrity of %s with keys from %s" % (portage_tree, key_location)
            ret = os.system(gemato_cmd)
    return ret
