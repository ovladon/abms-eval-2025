# publisher/analysis_modules/specificity_analysis.py

from .base_pov import BasePOV
import nltk
from nltk.corpus import wordnet as wn
from nltk import word_tokenize

class SpecificityAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)

    def analyze(self):
        words = word_tokenize(self.text.lower())
        specificity_scores = []
        for word in words:
            synsets = wn.synsets(word)
            if synsets:
                depths = [synset.max_depth() for synset in synsets]
                specificity = max(depths)
                specificity_scores.append(specificity)
        average_specificity = sum(specificity_scores) / len(specificity_scores) if specificity_scores else 0
        normalized_score = average_specificity / 20  # Assuming max depth is 20
        return {'specificity_analysis': normalized_score}

