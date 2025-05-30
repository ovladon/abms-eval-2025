# publisher/analysis_modules/interactivity_analysis.py
from __future__ import annotations
from .base_pov import BasePOV
import re, pathlib, spacy, functools

# ── load spaCy once, lazily ─────────────────────────────────────────────
@functools.lru_cache(maxsize=1)
def _get_nlp():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        # Automatic download the first time – avoids silent zero-scores.
        from spacy.cli import download
        download("en_core_web_sm")
        return spacy.load("en_core_web_sm")


class InteractivityAnalysis(BasePOV):
    """Questions + calls-to-action + 2nd-person pronouns"""

    CTA_PHRASES = {
        "click here", "sign up", "join us", "contact us", "learn more",
        "subscribe", "get started", "buy now",
    }
    _cta_re = re.compile("|".join(re.escape(p) for p in CTA_PHRASES), re.I)
    _you_re = re.compile(r"\byou\b", re.I)

    def analyze(self) -> dict[str, float]:
        nlp = _get_nlp()
        doc = nlp(self.text)

        q = sum(1 for s in doc.sents if s.text.strip().endswith("?"))
        cta = len(self._cta_re.findall(self.text))
        second_person = len(self._you_re.findall(self.text))

        sent_count = max(1, len(list(doc.sents)))  # avoid /0
        score = (q + cta + second_person) / sent_count
        return {"interactivity_analysis": round(score, 4)}
