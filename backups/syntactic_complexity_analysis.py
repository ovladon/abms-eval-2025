# publisher/analysis_modules/syntactic_complexity_analysis.py

from .base_pov import BasePOV
import spacy

nlp = spacy.load('en_core_web_sm')

class SyntacticComplexityAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)

    def analyze(self):
        doc = nlp(self.text)
        noun_phrases = list(doc.noun_chunks)
        modifier_counts = [len([token for token in np if token.dep_ == 'amod']) for np in noun_phrases]
        avg_modifiers = sum(modifier_counts) / len(modifier_counts) if modifier_counts else 0
        normalized_score = avg_modifiers / 10  # Normalize assuming max 10 modifiers
        return {'syntactic_complexity_analysis': normalized_score}

