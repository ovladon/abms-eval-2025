import json
import streamlit as st

class ContentSpeculator:
    def __init__(self, analysis_results):
        self.analysis_results = analysis_results
        self.knowledge_base = self.load_knowledge_base()

    def load_knowledge_base(self):
        try:
            with open('knowledge_base.json', 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            st.error(f"Error loading knowledge base: {e}")
            return {}

    def speculate_content(self, output_format='human'):
        categories = self.knowledge_base.get('topics', [])
        matched_categories = []
        for category in categories:
            if self.match_conditions(category['conditions']):
                if output_format == 'machine':
                    matched_categories.append({
                        'name': category['name'],
                        'machine_tags': category.get('machine_tags', []),
                        'confidence_score': category.get('confidence_score', 0.0)
                    })
                else:
                    matched_categories.append({
                        'name': category['name'],
                        'human_description': category.get('human_description', ''),
                        'keywords': category.get('keywords', []),
                        'references': category.get('references', []),
                        'confidence_score': category.get('confidence_score', 0.0)
                    })
        return matched_categories

    def speculate_synergies(self, output_format='human'):
        synergies = self.knowledge_base.get('synergies', [])
        matched_synergies = []
        for synergy in synergies:
            if self.match_conditions(synergy['conditions']):
                if output_format == 'machine':
                    matched_synergies.append({
                        'name': synergy['name'],
                        'machine_tags': synergy.get('machine_tags', []),
                        'aspects_involved': synergy.get('aspects_involved', []),
                        'confidence_score': synergy.get('confidence_score', 0.0)
                    })
                else:
                    matched_synergies.append({
                        'name': synergy['name'],
                        'human_description': synergy.get('human_description', ''),
                        'aspects_involved': synergy.get('aspects_involved', []),
                        'references': synergy.get('references', []),
                        'confidence_score': synergy.get('confidence_score', 0.0)
                    })
        return matched_synergies

    def match_conditions(self, conditions):
        for aspect, condition in conditions.items():
            score = self.analysis_results.get(aspect)
            if score is None:
                return False
            if isinstance(condition, dict):
                min_val = condition.get('min', float('-inf'))
                max_val = condition.get('max', float('inf'))
                if not (min_val <= score <= max_val):
                    return False
            elif isinstance(condition, list):
                if not isinstance(score, list):
                    return False
                if not all(item in score for item in condition):
                    return False
            else:
                if score != condition:
                    return False
        return True

