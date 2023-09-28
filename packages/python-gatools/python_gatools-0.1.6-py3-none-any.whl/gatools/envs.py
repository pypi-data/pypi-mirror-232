import os
from pathlib import Path
from dotenv import load_dotenv

__ALL__ = ["load_fenv", "fenv"]


def load_fenv(path: str, fname: str = ".env"):
    load_dotenv(Path(path).parent / fname)


def fenv(fname, key):
    """ > ga.fenv(__file__, "ENVVAR") < """
    load_fenv(fname)
    return os.getenv(key)
