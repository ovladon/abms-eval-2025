import zlib
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def decode_aspect_based_metadata(aspect_based_metadata, encryption_key):
    # Decode from Base64.
    encrypted_data = base64.b64decode(aspect_based_metadata)
    iv = encrypted_data[:16]
    ct_bytes = encrypted_data[16:]

    # Decrypt and unpad the data.
    cipher = AES.new(encryption_key, AES.MODE_CBC, iv)
    compressed_data = unpad(cipher.decrypt(ct_bytes), AES.block_size)

    # Decompress the data.
    binary_bytes = zlib.decompress(compressed_data)
    binary_int = int.from_bytes(binary_bytes, byteorder='big')
    total_bits = get_total_bits()
    binary_data = bin(binary_int)[2:].zfill(total_bits)

    # Define the aspect order (with "data_hash" appended).
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
        'data_hash'  # Included to decode the data hash.
    ]

    analysis_results = {}
    index = 0

    for aspect in aspect_order:
        if aspect in numerical_aspects():
            min_value, max_value, bits = numerical_aspects()[aspect]
            binary_score = binary_data[index:index+bits]
            int_score = int(binary_score, 2)
            score = int_score / (2 ** bits - 1) * (max_value - min_value) + min_value
            analysis_results[aspect] = round(score, 2)
            index += bits
        elif aspect in categorical_aspects():
            category_mapping, bits = categorical_aspects()[aspect]
            binary_score = binary_data[index:index+bits]
            int_score = int(binary_score, 2)
            score = category_mapping.get(int_score, 'Unknown')
            analysis_results[aspect] = score
            index += bits
        elif aspect == "data_hash":
            # Decode 256 bits for the data hash.
            binary_score = binary_data[index:index+256]
            int_score = int(binary_score, 2)
            hash_hex = format(int_score, '064x')
            analysis_results[aspect] = hash_hex
            index += 256
        else:
            analysis_results[aspect] = 'Unknown'

    return {
        "analysis_results": analysis_results,
        "version": "1.0.0"
    }

def get_total_bits():
    total = 0
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
        'data_hash'
    ]
    for aspect in aspect_order:
        if aspect in numerical_aspects():
            _, _, bits = numerical_aspects()[aspect]
            total += bits
        elif aspect in categorical_aspects():
            _, bits = categorical_aspects()[aspect]
            total += bits
        elif aspect == "data_hash":
            total += 256
        else:
            total += 8
    return total

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
