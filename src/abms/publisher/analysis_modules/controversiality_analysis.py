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
        try:
            # Split the text into sentences
            sentences = sent_tokenize(self.text)
            
            if not sentences:
                return {'controversiality_analysis': 0.0}
            
            # Process each sentence individually
            scores = []
            for sentence in sentences:
                # Skip very short sentences
                if len(sentence.strip()) < 10:
                    continue
                    
                # Truncate sentence if it's too long
                if len(sentence) > 512:
                    sentence = sentence[:512]
                    
                try:
                    result = self.classifier(sentence)
                    label = result[0]['label']
                    score = int(label.split()[0])  # Extract the sentiment score (e.g., '3 stars')
                    scores.append(score)
                except Exception as e:
                    print(f"Error processing sentence: {e}")
                    continue
            
            # If we couldn't process any sentences, return 0
            if not scores:
                return {'controversiality_analysis': 0.0}
            
            # Compute controversiality as the standard deviation of sentiment scores
            if len(scores) > 1:
                # Standard deviation indicates disagreement/controversy
                controversiality = np.std(scores) / 2.0  # Normalize (max std dev is 2)
                
                # Also consider extreme sentiments as controversial
                extreme_count = sum(1 for s in scores if s == 1 or s == 5)
                extreme_ratio = extreme_count / len(scores)
                
                # Combine both metrics
                controversiality = (controversiality * 0.7 + extreme_ratio * 0.3)
                controversiality = min(controversiality, 1.0)
                controversiality = round(float(controversiality), 2)
            else:
                # Single sentence - check if it's extreme
                if scores[0] in [1, 5]:
                    controversiality = 0.5
                else:
                    controversiality = 0.0
                    
            return {'controversiality_analysis': controversiality}
            
        except Exception as e:
            print(f"Error in controversiality analysis: {e}")
            return {'controversiality_analysis': 0.0}
