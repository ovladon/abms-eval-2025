# publisher/analysis_modules/controversiality_analysis.py

from .base_pov import BasePOV
from transformers import pipeline
from nltk.tokenize import sent_tokenize
import numpy as np

class ControversialityAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)
        # Using a sentiment analysis model to detect strong negative sentiments
        self.classifier = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
        # Ensure NLTK punkt tokenizer is available
        import nltk
        nltk.download('punkt', quiet=True)

    def analyze(self):
        # Split the text into sentences
        sentences = sent_tokenize(self.text)
        # Process each sentence individually
        scores = []
        for sentence in sentences:
            # Truncate sentence if it's too long
            if len(sentence) > 512:
                sentence = sentence[:512]
            result = self.classifier(sentence)
            label = result[0]['label']
            score = int(label.split()[0])  # Extract the sentiment score (e.g., '3 stars')
            scores.append(score)
        # Compute controversiality as the standard deviation of sentiment scores
        if scores:
            controversiality = np.std(scores) / 2.0  # Normalize between 0 and 1 (since std dev can be up to 2)
            controversiality = min(controversiality, 1.0)
            controversiality = round(controversiality, 2)
        else:
            controversiality = 0.0
        return {'controversiality_analysis': controversiality}

