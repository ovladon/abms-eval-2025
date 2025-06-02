# publisher/analysis_modules/lexical_diversity_analysis.py

from .base_pov import BasePOV
import nltk
from nltk.tokenize import word_tokenize
import string

class LexicalDiversityAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)
        # Ensure NLTK punkt tokenizer is available
        nltk.download('punkt', quiet=True)

    def analyze(self):
        try:
            # Tokenize and clean the text
            tokens = word_tokenize(self.text.lower())
            
            # Remove punctuation and non-alphabetic tokens
            words = [token for token in tokens 
                    if token.isalpha() and len(token) > 1]
            
            if not words:
                return {'lexical_diversity_analysis': 0.0}
            
            # Calculate Type-Token Ratio (TTR)
            unique_words = set(words)
            basic_ttr = len(unique_words) / len(words)
            
            # For longer texts, use MSTTR (Mean Segmental TTR)
            if len(words) > 100:
                window_size = 100
                window_step = 50
                ttrs = []
                
                for i in range(0, len(words) - window_size + 1, window_step):
                    window = words[i:i + window_size]
                    window_ttr = len(set(window)) / len(window)
                    ttrs.append(window_ttr)
                
                if ttrs:
                    msttr = sum(ttrs) / len(ttrs)
                else:
                    msttr = basic_ttr
                    
                diversity_score = msttr
            else:
                # For short texts, use basic TTR with adjustment
                # Adjust for text length bias
                length_adjustment = min(1.0, len(words) / 100)
                diversity_score = basic_ttr * (0.7 + 0.3 * length_adjustment)
            
            # Ensure score is between 0 and 1
            diversity_score = max(0.0, min(1.0, diversity_score))
            
            return {'lexical_diversity_analysis': float(diversity_score)}
            
        except Exception as e:
            print(f"Error in lexical diversity analysis: {e}")
            return {'lexical_diversity_analysis': 0.0}
