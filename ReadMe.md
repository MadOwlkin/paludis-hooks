# Paludis-hooks
This repository contains some paludis-hooks. Maybe they are useful for someone. At the moment the repository contains the following hooks:

## gemato-verify.py

A simple hook, which just uses app-portage/gemato to verify the authenticity of the main gentoo repository after a sync. Please note that you should use either this hook or btrfs_supported_gemato.py, never both. This hook is the boring, safe hook.

### Usage
* Copy gemato-verify.py to /etc/paludis/hooks/sync_all_post/

## btrfs_supported_gemato.py

A little experiment, which got a bit out of hand, this hooks is optionally able to use btrfs to roll the repository back if authenticity could not be established. Additionally it allows verification for other repositories than the main repository. It uses a JSON config file which it expects at /etc/paludis/authenticated_repositories.json. In this file one can configure handling per repository, using the name as key.

Example config for the gentoo main repository, using btrfs for being able to roll back the tree

    {
        "gentoo": {
                "device": "/dev/sda6",
                "mntpoint": "/usr/portage",
                "subvol": "portage",
                "key_location": "/var/lib/gentoo/gkeys/keyrings/gentoo/release/pubring.gpg",
                "method": "btrfs",
                "enabled": "true"
        }
    }
    
The options possible are:
* __device__: The device which hosts the btrfs volume with the ebuild repository. The hook expects to have a volume named snapshots there and a subvolume, which name is given in 'subvol', containing the ebuild repository
* __enabled__: The hook only acts on this entry, if enabled is true. Default is false.
* __key_location__: Location for the keyring to be used to verify the repository
* __method__: The way to verify the repository, at the moment there are two values supported
    * __btrfs__: Make a snapshot before syncing and roll back if authentication fails
    * __plain__: Just do authentication of the repository in question
* __mntpoint__: Mountpoint the repository is mounted to (in case of btrfs support, so that it can be remounted for rollback)
* __subvol__: Name of the subvolume on 'device' containing the repository

### Caveats

This hook is working for me since some time, but it didn't have much testing in sense of "Things going horribly wrong". As it is manipulating btrfs subvolumes there is a possible risk. This hook is provided in the hope of being useful, but you use it completly on your own, with no implication given that it won't break something.

### Known problems

Using btrfs-method:
* If paludis crashes mid-syncing, then there will be a snapshot left and generating the new one will fail next sync

### Usage

* Copy hooks/sync_all_pre/btrfs_supported_gemato.py to /etc/paludis/hooks/sync_all_pre
* Copy hooks/sync_all_post/btrfs_supported_gemato.py to /etc/paludis/hooks/sync_all_post
* Copy hooks/python_helpers/btrfs.py /etc/paludis/hooks/python_helpers/btrfs.py
* Create a configuration in /etc/paludis/authenticated_repositories.json

## Requirements

All hooks:

* app-portage/gemato
* dev-lang/python

btrfs_supported_gemato.py:

* sys-fs/btrfs-progs

## Hooks license

The hooks are released under MIT license.
