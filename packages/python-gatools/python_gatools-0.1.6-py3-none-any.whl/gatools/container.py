from collections import defaultdict
import os
import pathlib
import shutil

import numpy as np

from gatools.commons import dump_json, load_json
from gatools.files import Tree, fTree

    # def __init__(self, a, clean=False, **kw):
    #     super().__init__(a)
class Container(Tree):
    def __new__(cls, *args, **kwargs):
        args = list(args)
        fname = args[0]
        clean = kwargs.pop("clean", False)
        tree = super().__new__(cls, *args, **kwargs)

        if clean:
            s = input(f"Remove {fname} (y|n) ? ")
            if s == 'y':
                shutil.rmtree(fname)
        tree.mkdir()
        assert os.path.isdir(fname)

        tree.s = []

        return tree

        # self.dump(clean=clean)
        # self.infos = {}
        # fname = os.path.join(self.root / "infos.tree")
        # if os.path.isfile(fname):
        #     obj = Tree.from_file(fname)
        #     obj.copy_init_(self)
        # self.root = os.path.dirname(fname)

    def __truediv__(self, other):
        ds = other.split(os.path.sep)
        if len(ds) == 1 and os.path.splitext(ds[0])[1] == "":
            raise RuntimeError(
                "You cannot use '/' for directories in containers, use sep in strings: out / 'smth/fname.p'"
            )
        else:
            aze = os.path.splitext(ds[-1])[0]
            if hasattr(self, aze) and getattr(self, aze) == self.path(other):
                return super().__truediv__(other)
            self.s.append(os.path.join(self, os.path.sep.join(ds)))
            os.makedirs(os.path.join(self, os.path.sep.join(ds[:-1])), exist_ok=True)
            # o = self
            # for x in ds[:-1]:
            #     o = o.dir(x)
            # o.dump()
            # # self.infos[ds[-1]] = other
            # o.file(ds[-1])
        return super().__truediv__(other)

    def __enter__(self):
        fname = Tree(self) / "container_infos.json"
        if fname.is_file():
            self.s = load_json(fname)["files"]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()

    def save(self):
        fname = os.path.join(self, "container_infos.json")
        dump_json(fname, {"files": list(set(self.s))})
        


