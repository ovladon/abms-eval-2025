# publisher/analysis_modules/reliability_analysis.py
from __future__ import annotations
from .base_pov import BasePOV
import functools, logging, torch
from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModelForSequenceClassification,
)

_MODEL = "facebook/bart-large-mnli"          # 4× smaller than DeBERTa-XL
_DEVICE = 0 if torch.cuda.is_available() else -1


# ────────────────────────────────────────────────────────────────────
#  One-time download (protected by your global retry hook)
# ────────────────────────────────────────────────────────────────────
@functools.lru_cache(maxsize=1)
def _ensure_cached():
    logging.info("[ABMS] ensuring reliability model is cached …")
    AutoTokenizer.from_pretrained(_MODEL)                      # may download
    AutoModelForSequenceClassification.from_pretrained(_MODEL) # may download


# ────────────────────────────────────────────────────────────────────
#  Build zero-shot pipeline from *objects*  → no stray kwargs
# ────────────────────────────────────────────────────────────────────
@functools.lru_cache(maxsize=1)
def _get_pipe():
    _ensure_cached()
    tok = AutoTokenizer.from_pretrained(_MODEL)
    mdl = AutoModelForSequenceClassification.from_pretrained(_MODEL)
    return pipeline(
        "zero-shot-classification",         # ← correct task
        model=mdl,
        tokenizer=tok,
        device=_DEVICE,
    )


# ────────────────────────────────────────────────────────────────────
#  Analysis class
# ────────────────────────────────────────────────────────────────────
class ReliabilityAnalysis(BasePOV):
    """
    Approximates factual reliability as P(ENTAILMENT) for the hypothesis
    “This statement is factually correct.”
    """

    _HYP = "The statement is {}."

    def analyze(self):
        pipe = _get_pipe()
        out = pipe(
            self.text[:512],
            candidate_labels=["yes"],          # dummy label
            hypothesis_template=self._HYP,
        )
        # zero-shot pipeline returns a dict with 'scores' parallel to labels
        score = float(out["scores"][0])        # prob. hypothesis entailed
        return {"reliability_analysis": round(score, 4)}
