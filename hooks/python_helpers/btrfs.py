import os
import subprocess
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

    def snapshot(self, source, snapname, read_only = True):
        if self.tmpmnt is None:
            raise Error('btrfs control mount is not established')

        btrfs_args = [ 'subvolume', 'snapshot', '%s/%s' % (self.tmpmnt, source), '%s/%s' % (self.tmpmnt, snapname) ]

        if read_only == True:
            btrfs_args.append('-r')

        with open(os.devnull, 'wb') as devnull:
            subprocess.check_call(['/sbin/btrfs'] + btrfs_args, stdout=devnull)

    def rollback(self, source, target, subvol = None):
        if self.tmpmnt is None:
            raise Error('btrfs control mount is not established')
        self.rm_snapshot(target)
        self.snapshot(source, target, False)
        mnt_handle = MntWrapper(self.source, self.target)
        mnt_handle.umount()
        if subvol == None:
            subvol_option = 'subvol=%s' % target
        else:
            subvol_option = 'subvol=%s' % subvol
        mnt_handle.mount(subvol_option)

    def rm_snapshot(self, snapname):
        if self.tmpmnt is None:
            raise Error('btrfs control mount is not established')

        btrfs_args = [ 'subvolume', 'delete', '%s/%s' % (self.tmpmnt, snapname) ]

        with open(os.devnull, 'wb') as devnull:
            subprocess.check_call(['/sbin/btrfs'] + btrfs_args, stdout=devnull)
