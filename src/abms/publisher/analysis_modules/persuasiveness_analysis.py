# publisher/analysis_modules/persuasiveness_analysis.py

from .base_pov import BasePOV
import string

class PersuasivenessAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)
        self.persuasive_keywords = set([
            "must", "need", "should", "clearly", "obviously", "therefore",
            "consequently", "undoubtedly", "certainly", "definitely",
            "absolutely", "essential", "crucial", "vital", "important",
            "significant", "compelling", "irrefutable", "unquestionably",
            "best", "worst", "proven", "evidence", "research", "studies",
            "demonstrate", "show", "because", "since", "as a result", "thus",
            "hence", "furthermore", "moreover", "in addition", "support",
            "benefit", "advantage", "disadvantage"
            # Add more persuasive words and phrases as needed
        ])
        self.emphasis_punctuations = ['!', '?']

    def analyze(self):
        text = self.text.lower()
        translator = str.maketrans('', '', string.punctuation.replace('!', '').replace('?', ''))
        text_no_punct = text.translate(translator)
        words = text_no_punct.split()

        total_words = len(words)
        if total_words == 0:
            return {'persuasiveness_analysis': 0.0}

        persuasive_keyword_count = sum(1 for word in words if word in self.persuasive_keywords)
        emphasis_punct_count = sum(text.count(punct) for punct in self.emphasis_punctuations)

        keyword_score = persuasive_keyword_count / total_words
        punctuation_score = min(emphasis_punct_count * 0.05, 0.1)
        persuasiveness_score = keyword_score + punctuation_score
        persuasiveness_score = min(persuasiveness_score, 1.0)

        return {'persuasiveness_analysis': persuasiveness_score}

