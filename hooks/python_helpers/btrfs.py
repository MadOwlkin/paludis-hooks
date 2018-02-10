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
    def __init__(self, source):
        self.source = source

    def __enter__(self):
        self.tmpmnt = tempfile.mkdtemp()
        self.mntpoint = MntWrapper(self.source, self.tmpmnt)
        self.mntpoint.mount()

        return self.tmpmnt

    def __exit__(self, type, value, traceback):
        self.mntpoint.umount()
        os.rmdir(self.tmpmnt)
