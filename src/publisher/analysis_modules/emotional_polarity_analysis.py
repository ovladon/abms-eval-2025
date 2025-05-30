# publisher/analysis_modules/emotional_polarity_analysis.py

from .base_pov import BasePOV
from transformers import pipeline

emotion_pipeline = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)

class EmotionalPolarityAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)

    def analyze(self):
        results = emotion_pipeline(self.text[:512])
        emotions = results[0]
        max_emotion = max(emotions, key=lambda x: x['score'])
        return {'emotional_polarity_analysis': max_emotion['score']}

