import glob
import os
import pathlib
import shutil

__ALL__ = ["Tree", "fTree", "removeIfExists", "remove", "move"]


class Tree(type(pathlib.Path())):
    def mkdir(self, parents=True, exist_ok=True):
        super().mkdir(parents=parents, exist_ok=exist_ok)
        return self


class fTree(Tree):
    def __new__(cls, *args, **kwargs):
        args = list(args)
        if (x := pathlib.Path(args[0])).is_file():
            args[0] = x.parent
        return super().__new__(cls, *args, **kwargs)


def removeIfExists(fname: str):
    """Remove `fname` if it exists"""
    if os.path.exists(fname):
        os.remove(fname)


def remove(*args: str):
    """Remove files in globs `*args` if they exist"""
    for t in args:
        for f in glob.glob(t):
            removeIfExists(f)


def move(arg: str, dest: str):
    """Move files in glob `arg` to `dest` with `shutil.move`"""
    from gatools.strings import Str
    for f in glob.glob(arg):
        removeIfExists(os.path.join(dest, os.path.basename(f)))
        shutil.move(f, Str(dest))
