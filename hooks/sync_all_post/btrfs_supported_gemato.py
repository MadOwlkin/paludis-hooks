import os
import subprocess
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

            gemato_args = [ 'verify', portage_tree, '-K', key_location, '-s' ]
            print "Verifying authenticity of %s with keys from %s" % (portage_tree, key_location)
            ret = subprocess.call(['/usr/bin/gemato'] + gemato_args)
            if data[name]['method'].encode('utf-8') == 'btrfs':
                ctrl = btrfs.BtrfsCtrl(device, portage_tree)
                with ctrl:
                    if ret == 1:
                        print "Authenticity check failed. Rolling back..."
                        ctrl.rollback('snapshots/snapshot_pre_sync', 'portage')
                    ctrl.rm_snapshot('snapshots/snapshot_pre_sync')
