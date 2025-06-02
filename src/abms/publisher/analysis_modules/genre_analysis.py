# publisher/analysis_modules/genre_analysis.py
from __future__ import annotations
from .base_pov import BasePOV
import functools, torch
from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModelForSequenceClassification,
)

_MODEL = "facebook/bart-large-mnli"
_DEVICE = 0 if torch.cuda.is_available() else -1

@functools.lru_cache(maxsize=1)
def _load():
    tok = AutoTokenizer.from_pretrained(_MODEL)
    mdl = AutoModelForSequenceClassification.from_pretrained(_MODEL)
    return pipeline(
        "zero-shot-classification",
        model=mdl,
        tokenizer=tok,
        device=_DEVICE,
    )

_LABELS = [
    "research article",
    "review",
    "editorial",
    "case study",
    "dataset paper",
]

class GenreAnalysis(BasePOV):
    def analyze(self):
        pipe = _load()
        res = pipe(
            self.text[:512],
            candidate_labels=_LABELS,
            hypothesis_template="This document is a {}.",
            top_k=1,
        )
        label = res["labels"][0]
        score = float(res["scores"][0])
        return {"genre": label, "genre_confidence": round(score, 4)}
