# -*- coding: utf-8 -*-
""" Working with subsets """
from logger import log_trace

DEFAULT = {
        "ASSERT",
        "PRINT",
        "PRINTF",
        "PRINTLN",
        "PRINTFLN",
        "WAIT",
        "INPUT",
        "EXIT",
        }

LOGOWNER = 'subsets'


def gen_subset(ubsub: dict, default: set[str] | None = None) -> dict:
    """ Generate subset translation dict """
    if not default:
        default = DEFAULT

    res: dict = {}
    if not isinstance(default, set):
        log_trace("Invalid argument 'default'. "
                  f"Expected set, got {type(default).__name__}",
                  TypeError, owner=LOGOWNER)
        return res

    if not ubsub:
        # autogenerate default
        return {k: k for k in default}
    if not isinstance(ubsub, dict):
        log_trace("Invalid argument 'ubsub'. "
                  f"Expected dict, got {type(ubsub).__name__}",
                  TypeError, owner=LOGOWNER)
        return res
    for item in default:
        key = ubsub.get(item)
        if not key:
            continue
        res[key] = item
    return res


DEFAULT_SUBSET = gen_subset(None)
