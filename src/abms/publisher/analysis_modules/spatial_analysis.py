# publisher/analysis_modules/spatial_analysis.py

from .base_pov import BasePOV
import spacy

nlp = spacy.load('en_core_web_sm')

class SpatialAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)

    def analyze(self):
        doc = nlp(self.text)
        locations = [ent.text for ent in doc.ents if ent.label_ in ['GPE', 'LOC']]
        unique_locations = set(locations)
        if len(unique_locations) > 10:
            scope = 'Global'
        elif len(unique_locations) > 3:
            scope = 'Regional'
        elif unique_locations:
            scope = 'Local'
        else:
            scope = 'General'
        return {'spatial_analysis': scope}

