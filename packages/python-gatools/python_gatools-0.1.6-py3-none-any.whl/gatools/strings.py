
import os
from typing import Callable

from gatools.files import Tree


class Str(str):
    def __new__(cls, value):
        if isinstance(value, Tree):
            value = value.abs()
        obj = str.__new__(cls, value)
        return obj

    def f(self, *a, **k):
        return Str(self.format(*a, **k))

    # @property
    # def parent(self) -> T:
    #     return Tree(os.path.dirname(os.path.abspath(self)))

    # @property
    # def basename(self) -> S:
    #     return os.path.basename(self)

    # @property
    # def sibling(self) -> Callable:
    #     return self.parent.path

    def join(self, *x):
        return Str(os.path.join(self, *x))

    # def isfile(self) -> bool:
    #     return os.path.isfile(self)

    # def isdir(self) -> bool:
    #     return os.path.isdir(self)

    def __truediv__(self, other):
        return self.join(other)

    # def glob(self, pattern: str) -> List[S]:
    #     return Tree(self).glob(pattern)

    # def dump(self) -> Tree:
    #     return Tree(self).dump()

    # def re(self, pat) -> StrReResult:
    #     m = re.search(rf"(.+)?{pat}_(\d+)(.+)?", self)
    #     if m:
    #         a, b, c = m[1], f"{pat}_{m[2]}", m[3]
    #         return StrReResult(int(m[2]), a, b, c)
