# publisher/analysis_modules/social_orientation_analysis.py

from .base_pov import BasePOV
import re

class SocialOrientationAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)

    def analyze(self):
        try:
            text_lower = self.text.lower()
            
            # Define social indicators with word boundaries
            collective_patterns = [
                r'\b(?:we|us|our|ours|ourselves)\b',
                r'\b(?:together|community|society|team|group|collective|everyone|everybody)\b',
                r'\b(?:people|public|citizens|members|colleagues|partners)\b',
                r'\b(?:collaborate|cooperation|partnership|unity|solidarity)\b',
                r'\b(?:common|shared|mutual|joint|collective)\b'
            ]
            
            individual_patterns = [
                r'\b(?:i|me|my|mine|myself)\b',
                r'\b(?:individual|personal|private|alone|self|solo)\b',
                r'\b(?:independent|autonomy|freedom|liberty)\b',
                r'\b(?:own|unique|distinct|separate)\b'
            ]
            
            # Count matches for each pattern
            collective_count = sum(len(re.findall(pattern, text_lower)) 
                                 for pattern in collective_patterns)
            individual_count = sum(len(re.findall(pattern, text_lower)) 
                                 for pattern in individual_patterns)
            
            total_social = collective_count + individual_count
            
            if total_social == 0:
                # No social indicators found - return neutral score
                return {'social_orientation_analysis': 0.5}
            
            # Calculate social orientation score
            # 0 = highly individual-oriented, 1 = highly collective-oriented
            social_score = collective_count / total_social
            
            # Apply smoothing to avoid extreme values for short texts
            word_count = len(text_lower.split())
            if word_count < 50:
                # For short texts, move score toward center
                social_score = 0.5 + (social_score - 0.5) * 0.7
            
            return {'social_orientation_analysis': float(social_score)}
            
        except Exception as e:
            print(f"Error in social orientation analysis: {e}")
            return {'social_orientation_analysis': 0.5}
