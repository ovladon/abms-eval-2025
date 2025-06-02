# publisher/analysis_modules/temporal_analysis.py

from .base_pov import BasePOV
import re
import spacy
from collections import Counter

nlp = spacy.load('en_core_web_sm')

class TemporalAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)

    def analyze(self):
        # Extract temporal expressions
        dates = re.findall(r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4})\b', self.text)
        # Analyze verb tenses
        doc = nlp(self.text)
        tenses = [token.tag_ for token in doc if token.pos_ == 'VERB']
        tense_counts = Counter(tenses)
        total_verbs = sum(tense_counts.values())
        past_tense_ratio = tense_counts.get('VBD', 0) / total_verbs if total_verbs else 0
        present_tense_ratio = tense_counts.get('VBP', 0) / total_verbs if total_verbs else 0
        future_tense_ratio = tense_counts.get('MD', 0) / total_verbs if total_verbs else 0
        temporal_score = (past_tense_ratio + present_tense_ratio + future_tense_ratio) / 3
        return {'temporal_analysis': temporal_score}

