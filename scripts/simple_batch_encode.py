#!/usr/bin/env python3
"""
Simple batch encoder that directly calls the Streamlit app's backend logic.
"""

import sys
import json
import pathlib
from tqdm import tqdm

# Add src to path
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

def extract_aspects_streamlit_style(text):
    """
    Extract aspects by calling the same logic as the Streamlit app.
    This mimics what happens when you upload text to the UI.
    """
    try:
        # Import the Streamlit app module
        import publisher.publisher_app as app
        
        # Look for the main processing function
        # Based on logs, it should be something like this:
        if hasattr(app, 'process_text_content'):
            return app.process_text_content(text)
        elif hasattr(app, 'generate_metadata'):
            return app.generate_metadata(text)
        elif hasattr(app, 'analyze_text'):
            return app.analyze_text(text)
        else:
            # Manual call to the metadata generator
            from publisher.aspect_based_metadata_generator import AspectBasedMetadataGenerator
            generator = AspectBasedMetadataGenerator()
            
            # Try different method names
            if hasattr(generator, 'generate_metadata'):
                return generator.generate_metadata(text)
            elif hasattr(generator, 'generate'):
                return generator.generate(text)
            elif hasattr(generator, 'analyze'):
                return generator.analyze(text)
            else:
                raise Exception("No suitable method found in AspectBasedMetadataGenerator")
                
    except Exception as e:
        print(f"Error extracting aspects: {e}")
        return {}


def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/simple_batch_encode.py input.jsonl output.jsonl")
        sys.exit(1)
        
    input_file, output_file = sys.argv[1:3]
    
    # Create output directory
    pathlib.Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Process line by line
    with open(input_file, 'r') as fin, open(output_file, 'w') as fout:
        lines = fin.readlines()
        
        for line in tqdm(lines, desc="Processing"):
            try:
                obj = json.loads(line.strip())
                
                if 'text' in obj:
                    aspects = extract_aspects_streamlit_style(obj['text'])
                    obj['aspects'] = aspects
                    
                fout.write(json.dumps(obj) + '\n')
                
            except Exception as e:
                print(f"Error processing line: {e}")
                # Write the original line without aspects
                fout.write(line)
                
    print(f"✓ Completed! Output written to {output_file}")


if __name__ == "__main__":
    main()
