import os
import imp
import json

def hook_run_sync_all_post(env, hook_env):
    with open('/etc/paludis/authenticated_repositories.json') as data_file:
        data = json.load(data_file)

    btrfs = imp.load_source('btrfs', '/etc/paludis/hooks/python_helpers/btrfs.py')
    targets = hook_env["TARGETS"].split(" ")
    for name in targets:
        if name in data:
            key_location = data[name]['key_location'].encode('utf-8')
            portage_tree = data[name]['mntpoint'].encode('utf-8')
            device = data[name]['device'].encode('utf-8')

            gemato_cmd = "gemato verify %s -K %s" % (portage_tree, key_location)
            print "Verifying integrity of %s with keys from %s" % (portage_tree, key_location)
            ret = os.system(gemato_cmd)
            if data[name]['method'].encode('utf-8') == 'btrfs':
                ctrl = btrfs.BtrfsCtrl(device)
                with ctrl as tmpmnt:
                    if ret == 1:
                        snapshot_cmd = "btrfs subvolume delete %s/portage" % tmpmnt
                        os.system(snapshot_cmd)
                        snapshot_cmd = "btrfs subvolume snapshot %s/snapshots/snapshot_pre_sync %s/portage" % (tmpmnt, tmpmnt)
                        os.system(snapshot_cmd)
                        mnt_handle = btrfs.MntWrapper(device, portage_tree)
                        mnt_handle.umount()
                        mnt_handle.mount('subvol=portage')
                    snapshot_cmd = "btrfs subvolume delete %s/snapshots/snapshot_pre_sync" % tmpmnt
                    os.system(snapshot_cmd)
