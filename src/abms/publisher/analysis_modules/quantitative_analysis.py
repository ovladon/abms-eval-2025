# publisher/analysis_modules/quantitative_analysis.py

from .base_pov import BasePOV
import re

class QuantitativeAnalysis(BasePOV):
    def __init__(self, text):
        super().__init__(text)

    def analyze(self):
        try:
            word_count = len(self.text.split())
            if word_count == 0:
                return {'quantitative_analysis': 0.0}
            
            quant_count = 0
            
            # 1. Numbers (integers and decimals)
            numbers = re.findall(r'\b\d+(?:\.\d+)?\b', self.text)
            quant_count += len(numbers)
            
            # 2. Percentages
            percentages = re.findall(r'\b\d+(?:\.\d+)?%', self.text)
            quant_count += len(percentages) * 2  # Weight percentages higher
            
            # 3. Fractions
            fractions = re.findall(r'\b\d+/\d+\b', self.text)
            quant_count += len(fractions)
            
            # 4. Ordinals
            ordinal_patterns = [
                r'\b(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\b',
                r'\b\d+(?:st|nd|rd|th)\b'
            ]
            for pattern in ordinal_patterns:
                ordinals = re.findall(pattern, self.text.lower())
                quant_count += len(ordinals)
            
            # 5. Quantitative comparisons
            comparison_patterns = [
                r'\b(?:more|less|fewer|greater|higher|lower|bigger|smaller|larger)\s+than\b',
                r'\b(?:increase|decrease|rise|fall|growth|decline)\s+(?:of|by)\s+\d+',
                r'\b(?:double|triple|quadruple|half|quarter)\b',
                r'\b(?:majority|minority|most|least|few|many|several)\b'
            ]
            for pattern in comparison_patterns:
                comparisons = re.findall(pattern, self.text.lower())
                quant_count += len(comparisons)
            
            # 6. Statistical terms
            stat_terms = ['average', 'mean', 'median', 'mode', 'range', 
                         'standard deviation', 'variance', 'correlation',
                         'percentage', 'ratio', 'proportion', 'rate',
                         'probability', 'frequency', 'distribution']
            for term in stat_terms:
                if term in self.text.lower():
                    quant_count += 2  # Weight statistical terms
            
            # 7. Measurement units
            units_pattern = r'\b\d+(?:\.\d+)?\s*(?:kg|g|mg|lb|oz|m|km|cm|mm|ft|in|l|ml|gal|°[CF]|mph|kph|Hz|kHz|MHz|GB|MB|KB)\b'
            measurements = re.findall(units_pattern, self.text)
            quant_count += len(measurements) * 2  # Weight measurements
            
            # 8. Mathematical expressions
            math_patterns = [
                r'[+\-*/=<>≤≥±∞∑∏∫]',  # Mathematical operators
                r'\b(?:equals?|plus|minus|times|divided by|sum|product)\b'
            ]
            for pattern in math_patterns:
                math_expr = re.findall(pattern, self.text.lower())
                quant_count += len(math_expr)
            
            # Calculate normalized score
            # Adjust the multiplier based on typical quantitative density
            normalized_score = min(quant_count / word_count * 8, 1.0)
            
            return {'quantitative_analysis': float(normalized_score)}
            
        except Exception as e:
            print(f"Error in quantitative analysis: {e}")
            return {'quantitative_analysis': 0.0}
