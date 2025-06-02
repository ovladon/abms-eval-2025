# publisher/analysis_modules/multimodality_analysis.py

from .base_pov import BasePOV

class MultimodalityAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)
        self.modalities = ['text', 'image', 'audio', 'video', 'interactive']
        # Keywords associated with each modality
        self.modality_keywords = {
            'image': ['image', 'picture', 'diagram', 'figure'],
            'audio': ['audio', 'sound', 'music', 'podcast'],
            'video': ['video', 'animation', 'clip'],
            'interactive': ['interactive', 'simulation', 'game']
        }

    def analyze(self):
        text_lower = self.text.lower()
        modalities_present = []
        for modality, keywords in self.modality_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    modalities_present.append(modality)
                    break
        if modalities_present:
            multimodality = ', '.join(modalities_present)
        else:
            multimodality = 'text'
        return {'multimodality_analysis': multimodality}

