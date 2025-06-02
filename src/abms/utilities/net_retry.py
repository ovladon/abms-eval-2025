# src/abms/utilities/net_retry.py  – patch
from __future__ import annotations
import functools, logging, time, socket
from typing import Callable, Any

import huggingface_hub as _hf
from huggingface_hub import file_download as _fd
from urllib3.exceptions import NewConnectionError, MaxRetryError, NameResolutionError
from requests.exceptions import ConnectionError


def _retry_until_online(wait: int = 60) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def deco(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*a, **kw):  # type: ignore[override]
            attempt = 1
            while True:
                try:
                    return func(*a, **kw)
                except (
                    ConnectionError,
                    NewConnectionError,
                    MaxRetryError,
                    NameResolutionError,
                    socket.gaierror,
                ) as exc:
                    logging.warning(
                        "[ABMS] Internet unreachable while downloading HF asset "
                        f"(attempt {attempt}): {exc}. Sleeping %ss.", wait
                    )
                    attempt += 1
                    time.sleep(wait)
        return wrapper
    return deco


def _patch(obj, name: str, wait: int) -> None:
    if hasattr(obj, name):
        setattr(obj, name, _retry_until_online(wait)(getattr(obj, name)))


def install(wait: int = 60) -> None:
    """
    Wrap *any* hf-hub download entry-points that exist in the installed
    version.  Safe to call multiple times.
    """
    if getattr(_fd, "_abms_retry_installed", False):
        return

    # Always present
    _patch(_fd, "hf_hub_download", wait)

    # Optional – depends on version
    _patch(_hf, "snapshot_download", wait)      # top-level in ≥0.8
    _patch(_fd, "snapshot_download", wait)      # older nightly builds

    _fd._abms_retry_installed = True
    logging.info("[ABMS] Global HF retry hook active (wait=%s s)", wait)
