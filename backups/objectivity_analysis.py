# publisher/analysis_modules/objectivity_analysis.py

from .base_pov import BasePOV
from textblob import TextBlob

class ObjectivityAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)

    def analyze(self):
        blob = TextBlob(self.text)
        objectivity_score = 1 - blob.sentiment.subjectivity
        return {'objectivity_analysis': objectivity_score}

