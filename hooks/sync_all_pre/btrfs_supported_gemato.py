import os
import imp
import json

def hook_run_sync_all_pre(env, hook_env):
    targets = hook_env['TARGETS'].split(' ')
    btrfs = imp.load_source('btrfs', '/etc/paludis/hooks/python_helpers/btrfs.py')
    with open('/etc/paludis/authenticated_repositories.json') as data_file:
        data = json.load(data_file)

    for name in targets:
        if name in data:
            options = btrfs.RepositoryOptions(data[name])
            if not options.enabled():
                print('%s is configured, but disabled' % name)
                continue

            if options.method() == 'btrfs':
                print("Preparing btrfs rollback for %s" % name)
                ctrl = btrfs.BtrfsCtrl(options.device(), options.mntpoint())
                with ctrl:
                    ctrl.snapshot('portage', 'snapshots/snapshot_pre_sync')
