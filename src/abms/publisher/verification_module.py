# publisher/verification_module.py

import json
import zlib
import base64

class VerificationModule:
    def __init__(self, original_results, aspect_based_metadata):
        self.original_results = original_results
        self.aspect_based_metadata = aspect_based_metadata

    def verify(self):
        # Decode the aspect based metadata
        compressed_data = base64.b64decode(self.aspect_based_metadata.encode('utf-8'))
        json_str = zlib.decompress(compressed_data).decode('utf-8')
        unpacked_results = json.loads(json_str)
        # Compare original and unpacked results
        return self.original_results == unpacked_results

