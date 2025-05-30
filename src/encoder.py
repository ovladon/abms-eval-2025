# ────────────────────────────────────────────────────────────────────
#  src/abms/encoder.py
#  Complete, self-contained replacement (May-2025 edition)
# ────────────────────────────────────────────────────────────────────
"""
Create/extend *.tags.jsonl files with ABMS aspect scores.

Features
• Progress bar with ETA (tqdm)
• Crash-safe auto-resume (appends; skips docs already processed)
• Works fully offline when the env-vars
      HF_HUB_OFFLINE=1  TRANSFORMERS_OFFLINE=1
  are set and models are present in your HF cache
"""

from __future__ import annotations

import importlib
import json
import logging
import os
import pathlib
from types import ModuleType
from typing import Dict, List, Type

from tqdm import tqdm

# ----------------------------------------------------------------------
# configure logging (CLI may override)
# ----------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)

# ----------------------------------------------------------------------
# dynamically load every analysis module we ship
# ----------------------------------------------------------------------
_ANALYSIS_MODULES: List[Type] = []


def _discover_modules() -> None:
    """Populate _ANALYSIS_MODULES with every subclass of BasePOV found in
    abms.publisher.analysis_modules.*"""
    import pkgutil

    pkg = importlib.import_module("abms.publisher.analysis_modules")
    for modinfo in pkgutil.iter_modules(pkg.__path__, pkg.__name__ + "."):
        m: ModuleType = importlib.import_module(modinfo.name)
        for obj in m.__dict__.values():
            if isinstance(obj, type) and getattr(obj, "__base__", None):
                if obj.__base__.__name__ == "BasePOV":
                    _ANALYSIS_MODULES.append(obj)


_discover_modules()
logging.info("Loaded %d analysis modules: %s",
             len(_ANALYSIS_MODULES),
             [cls.__name__ for cls in _ANALYSIS_MODULES])

# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------
_CHUNK = 1 << 20  # 1 MiB


def _count_lines(fp: pathlib.Path, chunk: int = _CHUNK) -> int:
    """Fast line count without loading whole file into RAM."""
    with fp.open("rb") as fh:
        return sum(buf.count(b"\n") for buf in iter(lambda: fh.read(chunk), b""))


def _analyse(text: str) -> Dict[str, float | str]:
    """Run every aspect module on the given text."""
    out: Dict[str, float | str] = {}
    for Mod in _ANALYSIS_MODULES:
        try:
            for k, v in Mod(text).analyze().items():
                out[k] = v
        except Exception as e:  # noqa: BLE001
            logging.exception("Module %s failed; skipping (%s)", Mod.__name__, e)
    return out


# ----------------------------------------------------------------------
# public API
# ----------------------------------------------------------------------
def encode_file(in_path: pathlib.Path | str,
                out_path: pathlib.Path | str) -> None:
    """
    Read `in_path` (JSONL with a "text" field) and append aspect scores,
    writing/continuing `out_path`.

    The function is *idempotent*: re-running it after an interruption
    continues where it left off.
    """
    in_path = pathlib.Path(in_path)
    out_path = pathlib.Path(out_path)

    processed = 0
    if out_path.exists():
        processed = _count_lines(out_path)
        logging.info("Resuming: %d lines already encoded in %s",
                     processed, out_path.name)

    total = _count_lines(in_path)
    bar = tqdm(total=total,
               initial=processed,
               unit="doc",
               desc=in_path.name,
               dynamic_ncols=True)

    with in_path.open() as fin, out_path.open("a") as fout:
        # skip lines we already processed
        for _ in range(processed):
            next(fin)

        for line in fin:
            obj = json.loads(line)
            text = obj.get("text", "")
            obj["aspects"] = _analyse(text)
            fout.write(json.dumps(obj, ensure_ascii=False) + "\n")

            # flush every doc → minimal data loss on crash
            fout.flush()
            os.fsync(fout.fileno())

            bar.update()

    bar.close()
    logging.info("✓ done  %s  (%d docs)", out_path.name, total)
