# publisher/analysis_modules/lexical_diversity_analysis.py

from .base_pov import BasePOV
from nltk import word_tokenize
import numpy as np

class LexicalDiversityAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)

    def analyze(self):
        tokens = word_tokenize(self.text.lower())
        window_size = 50
        ttr_values = []
        for i in range(len(tokens) - window_size + 1):
            window = tokens[i:i + window_size]
            ttr = len(set(window)) / window_size
            ttr_values.append(ttr)
        mattr = np.mean(ttr_values) if ttr_values else 0
        return {'lexical_diversity_analysis': mattr}

