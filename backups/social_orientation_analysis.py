# publisher/analysis_modules/social_orientation_analysis.py

from .base_pov import BasePOV
import spacy

nlp = spacy.load('en_core_web_sm')

class SocialOrientationAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)

    def analyze(self):
        doc = nlp(self.text)
        pronouns = [token.text.lower() for token in doc if token.pos_ == 'PRON']
        individual_pronouns = {'i', 'me', 'my', 'mine', 'myself'}
        collective_pronouns = {'we', 'us', 'our', 'ours', 'ourselves'}
        individual_count = sum(pronouns.count(p) for p in individual_pronouns)
        collective_count = sum(pronouns.count(p) for p in collective_pronouns)
        total_pronouns = individual_count + collective_count
        if total_pronouns == 0:
            social_orientation_score = 0.5  # Neutral
        else:
            social_orientation_score = collective_count / total_pronouns
        return {'social_orientation_analysis': social_orientation_score}

