# publisher/analysis_modules/formalism_analysis.py

from .base_pov import BasePOV
import string

class FormalismAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)
        # Define a set of informal words and phrases
        self.informal_words = set([
            "u", "ur", "lol", "omg", "thx", "cya", "brb", "wanna", "gonna",
            "gotta", "ain't", "dunno", "kinda", "sorta", "imma", "gotcha",
            "btw", "idk", "ikr", "smh", "tbh", "gr8", "b4", "luv", "ya",
            "ttyl", "pls", "sup", "yo", "y'all", "gimme", "lemme", "k",
            "nvm", "cuz", "coz", "coulda", "woulda", "shoulda", "mighta",
            "wassup", "whatcha", "tryna", "doin'", "goin'", "havin'",
            "makin'", "talkin'", "lotta", "hafta", "needa", "lmk", "omw",
            "rofl", "plz", "tho", "thru", "ty", "wyd", "yolo", "bc",
            "imo", "irl", "jk", "np", "rn", "tbf", "ttys", "bruh", "fam"
            # Add more informal words as needed
        ])

    def analyze(self):
        # Convert text to lowercase and remove punctuation
        translator = str.maketrans('', '', string.punctuation)
        text_clean = self.text.lower().translate(translator)
        words = text_clean.split()

        total_words = len(words)
        if total_words == 0:
            # Avoid division by zero; assume empty text is formal
            return {'formalism_analysis': 1.0}

        # Count the number of informal words in the text
        informal_count = sum(1 for word in words if word in self.informal_words)

        # Calculate formality score: higher score indicates more formality
        formality_score = 1 - (informal_count / total_words)

        return {'formalism_analysis': formality_score}

