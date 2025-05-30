# publisher/analysis_modules/ethical_considerations_analysis.py

from .base_pov import BasePOV
from transformers import pipeline

# Initialize the zero-shot-classification pipeline
ethical_pipeline = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

class EthicalConsiderationsAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)

    def analyze(self):
        premise = self.text[:512]
        labels = ["Ethical", "Unethical", "Neutral"]
        result = ethical_pipeline(premise, candidate_labels=labels)
        scores = dict(zip(result['labels'], result['scores']))

        unethical_score = scores.get('Unethical', 0)

        # Map the unethical score to 'Low', 'Medium', 'High'
        if unethical_score > 0.6:
            level = 'High'
        elif unethical_score > 0.3:
            level = 'Medium'
        else:
            level = 'Low'

        return {'ethical_considerations_analysis': level}

