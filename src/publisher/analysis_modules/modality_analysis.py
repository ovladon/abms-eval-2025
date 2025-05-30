# publisher/analysis_modules/modality_analysis.py

from .base_pov import BasePOV

class ModalityAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)
        self.modalities = ['Textual', 'Visual', 'Auditory', 'Multimedia']
        # Keywords associated with each modality
        self.modality_keywords = {
            'Textual': ['read', 'write', 'text', 'book'],
            'Visual': ['see', 'look', 'image', 'picture', 'visualize'],
            'Auditory': ['hear', 'listen', 'sound', 'music'],
            'Multimedia': ['video', 'animation', 'interactive', 'media']
        }

    def analyze(self):
        text_lower = self.text.lower()
        modality_scores = {modality: 0 for modality in self.modalities}
        for modality, keywords in self.modality_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    modality_scores[modality] += 1
        # Select the modality with the highest score
        modality = max(modality_scores, key=modality_scores.get)
        # If no keywords are found, default to 'Textual'
        if modality_scores[modality] == 0:
            modality = 'Textual'
        return {'modality_analysis': modality}

