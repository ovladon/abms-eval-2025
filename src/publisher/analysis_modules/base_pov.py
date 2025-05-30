# publisher/analysis_modules/base_pov.py

class BasePOV:
    def __init__(self, text):
        self.text = text

    def analyze(self):
        raise NotImplementedError("Subclasses should implement this method.")

