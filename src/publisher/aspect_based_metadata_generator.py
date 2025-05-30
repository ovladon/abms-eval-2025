import zlib
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def generate_aspect_based_metadata(analysis_results, encryption_key):
    # Define the order of aspects and include "data_hash" at the end.
    aspect_order = [
        'actionability_analysis',
        'audience_appropriateness_analysis',
        'cognitive_analysis',
        'complexity_analysis',
        'controversiality_analysis',
        'cultural_context_analysis',
        'emotional_polarity_analysis',
        'ethical_considerations_analysis',
        'formalism_analysis',
        'genre_analysis',
        'humor_analysis',
        'intentionality_analysis',
        'interactivity_analysis',
        'lexical_diversity_analysis',
        'modality_analysis',
        'multimodality_analysis',
        'narrative_style_analysis',
        'novelty_analysis',
        'objectivity_analysis',
        'persuasiveness_analysis',
        'quantitative_analysis',
        'qualitative_analysis',
        'readability_analysis',
        'reliability_analysis',
        'sentiment_analysis',
        'social_orientation_analysis',
        'specificity_analysis',
        'spatial_analysis',
        'syntactic_complexity_analysis',
        'temporal_analysis',
        'data_hash'  # Added to include the data hash
    ]

    binary_data = ''

    for aspect in aspect_order:
        if aspect == "data_hash":
            # Encode the data hash (a 64-character hex string representing 256 bits).
            hash_str = analysis_results.get("data_hash")
            if hash_str is None:
                hash_int = 0
            else:
                hash_int = int(hash_str, 16)
            binary_score = format(hash_int, '0256b')  # 256 bits padded with zeros
        elif aspect in numerical_aspects():
            score = analysis_results.get(aspect)
            if score is None:
                print(f"Aspect '{aspect}' is missing in analysis_results. Defaulting to zero.")
                score = numerical_aspects()[aspect][0]  # Default to min value
            print(f"Processing aspect '{aspect}' with score '{score}'")
            min_value, max_value, bits = numerical_aspects()[aspect]
            try:
                score = float(score)
                score = max(min_value, min(score, max_value))
                normalized_score = int((score - min_value) / (max_value - min_value) * (2 ** bits - 1))
                binary_score = format(normalized_score, f'0{bits}b')
            except (ValueError, TypeError) as e:
                print(f"Error encoding numerical aspect '{aspect}': {e}")
                return None
        elif aspect in categorical_aspects():
            score = analysis_results.get(aspect)
            category_mapping, bits = categorical_aspects()[aspect]
            int_score = None
            for key, value in category_mapping.items():
                if value == score:
                    int_score = key
                    break
            if int_score is None:
                print(f"Warning: Score '{score}' not found in mapping for aspect '{aspect}'. Defaulting to zero.")
                int_score = 0
            binary_score = format(int_score, f'0{bits}b')
        else:
            # For any unrecognized aspect, default to 8 bits of zeros.
            bits = 8
            binary_score = '0' * bits

        binary_data += binary_score

    # Convert binary string to bytes.
    try:
        binary_int = int(binary_data, 2)
        binary_bytes = binary_int.to_bytes((len(binary_data) + 7) // 8, byteorder='big')
    except ValueError as e:
        print(f"Error converting binary data to bytes: {e}")
        return None

    # Compress and then encrypt the data.
    compressed_data = zlib.compress(binary_bytes)
    cipher = AES.new(encryption_key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(compressed_data, AES.block_size))
    iv = cipher.iv
    encrypted_data = iv + ct_bytes

    # Encode with Base64.
    aspect_based_metadata = base64.b64encode(encrypted_data).decode('utf-8')
    return aspect_based_metadata

def numerical_aspects():
    return {
        'actionability_analysis': (0.0, 1.0, 16),
        'cognitive_analysis': (0.0, 20.0, 16),
        'complexity_analysis': (0.0, 1.0, 16),
        'controversiality_analysis': (0.0, 1.0, 16),
        'emotional_polarity_analysis': (0.0, 1.0, 16),
        'formalism_analysis': (0.0, 1.0, 16),
        'humor_analysis': (0.0, 1.0, 16),
        'interactivity_analysis': (0.0, 1.0, 16),
        'lexical_diversity_analysis': (0.0, 1.0, 16),
        'novelty_analysis': (0.0, 1.0, 16),
        'objectivity_analysis': (0.0, 1.0, 16),
        'persuasiveness_analysis': (0.0, 1.0, 16),
        'quantitative_analysis': (0.0, 1.0, 16),
        'qualitative_analysis': (0.0, 1.0, 16),
        'readability_analysis': (0.0, 100.0, 16),
        'reliability_analysis': (0.0, 1.0, 16),
        'sentiment_analysis': (-1.0, 1.0, 16),
        'social_orientation_analysis': (0.0, 1.0, 16),
        'specificity_analysis': (0.0, 1.0, 16),
        'syntactic_complexity_analysis': (0.0, 1.0, 16),
        'temporal_analysis': (0.0, 1.0, 16),
    }

def categorical_aspects():
    return {
        'audience_appropriateness_analysis': ({0: 'Children', 1: 'Middle School', 2: 'High School', 3: 'Adult'}, 2),
        'cultural_context_analysis': ({0: 'General', 1: 'Cultural Specific'}, 1),
        'ethical_considerations_analysis': ({0: 'Low', 1: 'Medium', 2: 'High'}, 2),
        'genre_analysis': ({0: 'Political Speech', 1: 'News', 2: 'Story', 3: 'Academic', 4: 'Legal', 5: 'Scientific', 6: 'Finance', 7: 'Entertainment', 8: 'Sports', 9: 'Historical Document'}, 4),
        'intentionality_analysis': ({0: 'Informative', 1: 'Persuasive', 2: 'Narrative', 3: 'Descriptive', 4: 'Expository', 5: 'Instructional'}, 3),
        'modality_analysis': ({0: 'Textual', 1: 'Visual', 2: 'Auditory', 3: 'Multimedia'}, 2),
        'multimodality_analysis': ({0: 'text', 1: 'image', 2: 'audio', 3: 'video', 4: 'interactive'}, 3),
        'narrative_style_analysis': ({0: 'First_Person', 1: 'Second_Person', 2: 'Third_Person'}, 2),
        'spatial_analysis': ({0: 'General', 1: 'Local', 2: 'Regional', 3: 'Global'}, 2),
    }
