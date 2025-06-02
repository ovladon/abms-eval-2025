# publisher/analysis_modules/quantitative_analysis.py

from .base_pov import BasePOV
import re

class QuantitativeAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)

    def analyze(self):
        numbers = re.findall(r'\b\d+(?:\.\d+)?(?:%| percent)?\b', self.text)
        statistical_terms = ['average', 'mean', 'median', 'mode', 'standard deviation', 'variance']
        stats_terms_count = sum(self.text.lower().count(term) for term in statistical_terms)
        total_words = len(self.text.split())
        quantitative_score = (len(numbers) + stats_terms_count) / total_words if total_words else 0
        return {'quantitative_analysis': quantitative_score}

