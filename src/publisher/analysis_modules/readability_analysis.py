# publisher/analysis_modules/readability_analysis.py
from __future__ import annotations
from .base_pov import BasePOV
import textstat, re

class ReadabilityAnalysis(BasePOV):
    """Flesch Reading Ease, mapped to [0,1]."""

    _cleanup_re = re.compile(r"\s+")

    def _preprocess(self, txt: str) -> str:
        # keep punctuation – textstat needs it for sentence detection
        txt = self._cleanup_re.sub(" ", txt.strip())
        return txt

    def analyze(self) -> dict[str, float]:
        clean = self._preprocess(self.text)
        try:
            raw = textstat.flesch_reading_ease(clean)  # -70…120 typical
        except Exception:
            raw = 0.0

        # map to 0–1 (high = easy).  <30 hard, >90 very easy
        clipped = max(0.0, min(raw, 100.0))
        score = round(clipped / 100.0, 4)
        return {"readability_analysis": score}
