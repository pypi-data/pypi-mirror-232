import logging
from collections import defaultdict

from munch import Munch, munchify


def analyse(d):
    # Analyse a list of dict
    r = defaultdict(list)
    for x in d:
        for k, v in x.items():
            r[k].append(v)
    return munchify(r)


def query(d, **kw):
    # Query a list of dict
    xkeep = []
    for x in d:
        cond = True
        for k, v in kw.items():
            if x.get(k) != v:
                cond = False
                break
        if cond:
            xkeep.append(x)
    if len(xkeep) == 1:
        return munchify(xkeep[0])
    return xkeep


def make_string(**kw):
    return "&".join([f"{k}={v}" for k, v in kw.items()])


def decode_string(s) -> Munch:
    return munchify({x.split("=")[0]: x.split("=")[1] for x in s.split("&")})


log = logging.getLogger(__name__)
