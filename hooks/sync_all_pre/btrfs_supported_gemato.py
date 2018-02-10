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
            if data[name]['method'].encode('utf-8') == 'btrfs':
                print "Preparing btrfs rollback for %s" % name
                ctrl = btrfs.BtrfsCtrl(data[name]['device'].encode('utf-8', 'ignore'), data[name]['mntpoint'].encode('utf-8'))
                with ctrl:
                    ctrl.snapshot('portage', 'snapshots/snapshot_pre_sync')
