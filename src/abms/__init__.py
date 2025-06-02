# src/abms/__init__.py
from .utilities import net_retry as _net_retry   # ← folder name here
_net_retry.install(wait=120)
