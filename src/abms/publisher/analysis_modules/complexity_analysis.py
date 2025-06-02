# publisher/analysis_modules/complexity_analysis.py

from .base_pov import BasePOV
import spacy
import textstat

nlp = spacy.load('en_core_web_sm')

class ComplexityAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)

    def analyze(self):
        doc = nlp(self.text)
        sentences = list(doc.sents)
        avg_sentence_length = textstat.avg_sentence_length(self.text)
        complex_words = textstat.difficult_words(self.text)
        total_words = len([token for token in doc if not token.is_punct])
        complex_word_percentage = (complex_words / total_words) * 100 if total_words else 0

        # Syntactic Complexity: Average Parse Tree Depth
        depths = [self.get_tree_depth(sent.root) for sent in sentences]
        avg_tree_depth = sum(depths) / len(depths) if depths else 0

        complexity_score = (avg_sentence_length + complex_word_percentage + avg_tree_depth) / 3
        normalized_score = complexity_score / 100  # Normalize to 0-1 range
        return {'complexity_analysis': normalized_score}

    def get_tree_depth(self, token):
        if not list(token.children):
            return 1
        else:
            return 1 + max(self.get_tree_depth(child) for child in token.children)

