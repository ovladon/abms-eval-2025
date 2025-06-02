# publisher/analysis_modules/specificity_analysis.py

from .base_pov import BasePOV
import re
import spacy

# Load the spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    import subprocess
    subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])
    nlp = spacy.load('en_core_web_sm')

class SpecificityAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)

    def analyze(self):
        try:
            doc = nlp(self.text)
            
            # Count various specificity indicators
            specificity_score = 0
            total_tokens = len(doc)
            
            if total_tokens == 0:
                return {'specificity_analysis': 0.0}
            
            # 1. Named entities (specific people, places, organizations)
            entities = list(doc.ents)
            entity_score = len(entities) / total_tokens * 10
            
            # 2. Numbers and quantitative expressions
            number_pattern = r'\b\d+(?:\.\d+)?(?:%|percent|dollars?|euros?|pounds?|kg|g|mg|m|km|cm|mm|l|ml|hours?|minutes?|seconds?|days?|weeks?|months?|years?)?\b'
            numbers = re.findall(number_pattern, self.text.lower())
            number_score = len(numbers) / total_tokens * 15
            
            # 3. Dates and times
            date_patterns = [
                r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',
                r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b',
                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{2,4}\b',
                r'\b\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{2,4}\b',
                r'\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?\b'
            ]
            date_count = sum(len(re.findall(pattern, self.text, re.IGNORECASE)) 
                            for pattern in date_patterns)
            date_score = date_count / total_tokens * 20
            
            # 4. Specific descriptors and modifiers
            specific_words = {'exactly', 'precisely', 'specifically', 'particular', 
                            'detailed', 'accurate', 'explicit', 'definite', 'certain',
                            'namely', 'especially', 'notably', 'specifically'}
            specific_count = sum(1 for token in doc 
                               if token.text.lower() in specific_words)
            descriptor_score = specific_count / total_tokens * 10
            
            # 5. Proper nouns (beyond named entities)
            proper_nouns = sum(1 for token in doc if token.pos_ == 'PROPN')
            proper_score = proper_nouns / total_tokens * 8
            
            # 6. Technical or domain-specific terms (approximated by less common words)
            technical_score = 0
            for token in doc:
                if (token.is_alpha and len(token.text) > 6 and 
                    not token.is_stop and token.pos_ in ['NOUN', 'ADJ']):
                    technical_score += 1
            technical_score = technical_score / total_tokens * 5
            
            # Combine all scores
            total_score = (entity_score + number_score + date_score + 
                          descriptor_score + proper_score + technical_score)
            
            # Normalize to 0-1 range
            specificity_score = min(total_score, 1.0)
            
            return {'specificity_analysis': float(specificity_score)}
            
        except Exception as e:
            print(f"Error in specificity analysis: {e}")
            return {'specificity_analysis': 0.0}
