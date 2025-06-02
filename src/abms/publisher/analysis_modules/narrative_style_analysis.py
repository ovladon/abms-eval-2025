# publisher/analysis_modules/narrative_style_analysis.py

from .base_pov import BasePOV
import spacy
from collections import Counter

nlp = spacy.load('en_core_web_sm')

class NarrativeStyleAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)

    def analyze(self):
        doc = nlp(self.text)
        pronouns = [token.text.lower() for token in doc if token.pos_ == 'PRON']
        pronoun_counts = Counter(pronouns)
        first_person = sum(pronoun_counts.get(p, 0) for p in ['i', 'we', 'me', 'us', 'my', 'our'])
        second_person = sum(pronoun_counts.get(p, 0) for p in ['you', 'your', 'yours'])
        third_person = sum(pronoun_counts.get(p, 0) for p in ['he', 'she', 'it', 'they', 'him', 'her', 'them', 'his', 'hers', 'their'])
        if first_person > max(second_person, third_person):
            style = 'First_Person'
        elif second_person > max(first_person, third_person):
            style = 'Second_Person'
        else:
            style = 'Third_Person'
        return {'narrative_style_analysis': style}

