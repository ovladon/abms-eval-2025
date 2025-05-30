# publisher/analysis_modules/intentionality_analysis.py

from .base_pov import BasePOV
from transformers import pipeline

intent_pipeline = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

class IntentionalityAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)

    def analyze(self):
        candidate_intents = ["Informative", "Persuasive", "Narrative", "Descriptive", "Expository", "Instructional"]
        result = intent_pipeline(self.text[:512], candidate_labels=candidate_intents)
        intent = result['labels'][0]
        return {'intentionality_analysis': intent}

