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
        try:
            doc = nlp(self.text)
            sentences = list(doc.sents)
            
            if not sentences:
                return {'actionability_analysis': 0.0}
            
            imperative_count = 0
            modal_count = 0
            
            # Modal verbs that indicate actionability
            modals = {'should', 'must', 'need', 'needs', 'have to', 'has to', 
                     'ought to', 'can', 'could', 'will', 'would', 'shall'}
            
            # Action verbs commonly used in imperatives
            action_verbs = {'do', 'make', 'create', 'build', 'implement', 'develop', 
                           'establish', 'improve', 'enhance', 'reduce', 'increase', 
                           'start', 'begin', 'stop', 'change', 'modify', 'update', 
                           'fix', 'solve', 'address', 'handle', 'ensure', 'check',
                           'verify', 'confirm', 'review', 'analyze', 'assess'}
            
            for sent in sentences:
                # Enhanced imperative detection
                if self.is_imperative_enhanced(sent, action_verbs):
                    imperative_count += 1
                
                # Check for modal verbs
                sent_text = sent.text.lower()
                for modal in modals:
                    if modal in sent_text:
                        modal_count += 1
                        break
            
            # Calculate composite score
            imperative_score = imperative_count / len(sentences)
            modal_score = min(modal_count / len(sentences), 1.0)
            
            # Weighted combination (imperatives are stronger indicators)
            actionability_score = (imperative_score * 0.6 + modal_score * 0.4)
            
            return {'actionability_analysis': float(actionability_score)}
            
        except Exception as e:
            print(f"Error in actionability analysis: {e}")
            return {'actionability_analysis': 0.0}

    def is_imperative_enhanced(self, sent, action_verbs):
        """Enhanced imperative detection"""
        if not sent or len(sent) == 0:
            return False
            
        # Get the first token
        first_token = sent[0]
        
        # Check if sentence starts with a base form verb
        if first_token.pos_ == 'VERB' and first_token.tag_ in ['VB', 'VBP']:
            return True
        
        # Check if first word (lowercased) is in our action verbs list
        first_word = first_token.text.lower()
        if first_word in action_verbs:
            return True
        
        # Check for imperative patterns with "please" or "kindly"
        sent_text = sent.text.lower()
        if sent_text.startswith(('please ', 'kindly ')):
            # Check if followed by a verb
            tokens = list(sent)
            if len(tokens) > 1 and tokens[1].pos_ == 'VERB':
                return True
        
        return False
