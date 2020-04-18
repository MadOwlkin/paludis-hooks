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
            options = btrfs.RepositoryOptions(data[name])

            if not options.enabled():
                print('%s is configured, but disabled' % name)
                continue

            gemato_args = [ 'verify', options.mntpoint(), '-K', options.key_location(), '-s' ]
            print("Verifying authenticity of %s with keys from %s" % (options.mntpoint(), options.key_location()))
            ret = subprocess.call(['/usr/bin/gemato'] + gemato_args)
            if options.method() == 'btrfs':
                ctrl = btrfs.BtrfsCtrl(options.device(), options.mntpoint())
                with ctrl:
                    if ret == 1:
                        print("Authenticity check failed. Rolling back...")
                        ctrl.rollback('snapshots/snapshot_pre_sync', options.subvol())
                    ctrl.rm_snapshot('snapshots/snapshot_pre_sync')
