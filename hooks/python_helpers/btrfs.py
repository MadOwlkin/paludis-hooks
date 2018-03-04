import os
import subprocess
import tempfile
import libmount as mnt

class RepositoryOptions:
    def __init__(self, options):
        if 'method' in options:
            self.__method = options['method'].encode('utf-8')
        else:
            self.__method = 'plain'
            print 'method not set, defaulting to %s' % self.__method
        if 'key_location' in options:
            self.__key_location = options['key_location'].encode('utf-8')
        else:
            self.__key_location = '/var/lib/gentoo/gkeys/keyrings/gentoo/release/pubring.gpg'
            print 'key_location not set, defaulting to %s' % self.__key_location
        if 'mntpoint' in options:
            self.__mntpoint = options['mntpoint'].encode('utf-8')
        else:
            self.__mntpoint = '/usr/portage'
            print 'mntpoint not set, defaulting to %s' % self.__mntpoint
        if 'enabled' in options:
            if options['enabled'].lower() in [ 'true', '1', 'yes' ]:
                self.__enabled = True
            else:
                self.__enabled = False
        else:
            self.__enabled = False
        if self.__method == 'btrfs':
            if 'device' in options:
                self.__device = options['device'].encode('utf-8')
            else:
                self.__device = None
                print 'device not set, unable to default to a sane value'
            if 'subvol' in options:
                self.__subvol = options['subvol'].encode('utf-8')
            else:
                self.__subvol = 'portage'
                print 'subvol not set, defaulting to %s' % self.__subvol
        else:
            self.__device = None
            self.__subvol = None

    def method(self):
        if self.__device == None:
            return 'plain'
        return self.__method

    def device(self):
        return self.__device

    def enabled(self):
        return self.__enabled

    def mntpoint(self):
        return self.__mntpoint

    def subvol(self):
        return self.__subvol

    def key_location(self):
        return self.__key_location

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
