from .base_pov import BasePOV
from transformers import pipeline

class HumorAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)
        # Using a fine-tuned DistilBERT model for joke detection
        self.classifier = pipeline("text-classification", model="VitalContribution/JokeDetectBERT")

    def analyze(self):
        # Limit text length to 512 characters for efficient processing
        input_text = self.text[:512]
        result = self.classifier(input_text)
        # The classifier returns a label and score; typically, 'LABEL_1' indicates a joke.
        label = result[0]['label']
        score = result[0]['score']
        # Compute humor score: use the score directly if labeled as joke,
        # otherwise, invert the score to reflect low humor.
        humor_score = score if label == 'LABEL_1' else 1 - score
        return {'humor_analysis': humor_score}
