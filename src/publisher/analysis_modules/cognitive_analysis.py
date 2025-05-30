# publisher/analysis_modules/cognitive_analysis.py

from .base_pov import BasePOV
import textstat

class CognitiveAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)

    def analyze(self):
        fk_grade = textstat.flesch_kincaid_grade(self.text)
        gunning_fog = textstat.gunning_fog(self.text)
        smog_index = textstat.smog_index(self.text)
        cognitive_score = (fk_grade + gunning_fog + smog_index) / 3
        return {'cognitive_analysis': cognitive_score}

