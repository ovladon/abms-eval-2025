# publisher/analysis_modules/qualitative_analysis.py

from .base_pov import BasePOV
import spacy

nlp = spacy.load('en_core_web_sm')

class QualitativeAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)

    def analyze(self):
        doc = nlp(self.text)
        adjectives_adverbs = [token for token in doc if token.pos_ in ['ADJ', 'ADV']]
        qualitative_score = len(adjectives_adverbs) / len(doc) if len(doc) > 0 else 0
        return {'qualitative_analysis': qualitative_score}

