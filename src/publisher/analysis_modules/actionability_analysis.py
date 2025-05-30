# publisher/analysis_modules/actionability_analysis.py

from .base_pov import BasePOV
import spacy

# Load the spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    # If the model is not found, download it
    import subprocess
    subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])
    nlp = spacy.load('en_core_web_sm')

class ActionabilityAnalysis(BasePOV):

    def __init__(self, text):
        super().__init__(text)
        
    def analyze(self):
        doc = nlp(self.text)
        imperative_sentences = [sent for sent in doc.sents if self.is_imperative(sent)]
        actionability_score = len(imperative_sentences) / len(list(doc.sents)) if doc.sents else 0
        return {'actionability_analysis': actionability_score}

    def is_imperative(self, sent):
        if not sent:
            return False
        # Check if the sentence starts with a verb in base form
        first_token = sent[0]
        if first_token.pos_ == 'VERB' and first_token.tag_ == 'VB':
            return True
        return False

