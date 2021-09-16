import os
from easyopt.lib import init, objective, report, should_prune

if "EASYOPT_SOCKET" in os.environ:
    init()