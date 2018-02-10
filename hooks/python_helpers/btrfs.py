import os
import tempfile
import libmount as mnt

class MntWrapper:
    def __init__(self, dev, mntpoint):
        self.dev = dev
        self.mntpoint = mntpoint

    def mount(self, options = None):
        ctx = mnt.Context()
        ctx.source = self.dev
        ctx.target = self.mntpoint
        if options is not None:
            ctx.options = options
        ctx.mount()

    def umount(self):
        ctx = mnt.Context()
        ctx.target = self.mntpoint
        ctx.umount()

class BtrfsCtrl:
    def __init__(self, source, target):
        self.source = source
        self.tmpmnt = None
        self.target = target

    def __enter__(self):
        self.tmpmnt = tempfile.mkdtemp()
        self.mntpoint = MntWrapper(self.source, self.tmpmnt)
        self.mntpoint.mount()

        return self

    def __exit__(self, type, value, traceback):
        self.mntpoint.umount()
        os.rmdir(self.tmpmnt)

    def snapshot(self, source, snapname):
        if self.tmpmnt is None:
            raise Error('btrfs control mount is not established')
        btrfs_cmd = 'btrfs subvolume snapshot -r %s/%s %s/%s' % (self.tmpmnt, source, self.tmpmnt, snapname)
        os.system(btrfs_cmd)

    def rollback(self, source, target):
        if self.tmpmnt is None:
            raise Error('btrfs control mount is not established')
        btrfs_cmd = 'btrfs subvolume delete %s/%s' % (self.tmpmnt, target)
        os.system(btrfs_cmd)
        btrfs_cmd = 'btrfs subvolume snapshot %s/%s %s/%s' % (self.tmpmnt, source, self.tmpmnt, target)
        os.system(btrfs_cmd)
        mnt_handle = MntWrapper(self.source, self.target)
        mnt_handle.umount()
        mnt_handle.mount('subvol=portage')

    def rm_snapshot(self, snapname):
        if self.tmpmnt is None:
            raise Error('btrfs control mount is not established')
        btrfs_cmd = "btrfs subvolume delete %s/%s" % (self.tmpmnt, snapname)
        os.system(btrfs_cmd)
