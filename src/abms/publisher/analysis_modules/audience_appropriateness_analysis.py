# publisher/analysis_modules/audience_appropriateness_analysis.py

from .base_pov import BasePOV
import textstat

class AudienceAppropriatenessAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)

    def analyze(self):
        reading_level = textstat.flesch_kincaid_grade(self.text)
        if reading_level <= 5:
            audience_level = 'Children'
        elif reading_level <= 8:
            audience_level = 'Middle School'
        elif reading_level <= 12:
            audience_level = 'High School'
        else:
            audience_level = 'Adult'
        return {'audience_appropriateness_analysis': audience_level}

