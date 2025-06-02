#!/bin/bash
# Run these commands to understand the code structure

# 1. Find the main aspect extraction function
echo "=== Looking for aspect extraction functions ==="
grep -r "def.*aspect" src/ || echo "No aspect functions found with that pattern"

# 2. Check the aspect_based_metadata_generator.py content structure
echo -e "\n=== Checking aspect_based_metadata_generator.py ==="
head -30 src/publisher/aspect_based_metadata_generator.py

# 3. Look for the main entry point
echo -e "\n=== Looking for generate/extract functions ==="
grep -r "def generate\|def extract\|def analyze_text" src/publisher/ | head -10

# 4. Check what's imported in the main generator file
echo -e "\n=== Checking imports in generator ==="
grep -n "^import\|^from" src/publisher/aspect_based_metadata_generator.py | head -10

# 5. Look at analysis modules structure
echo -e "\n=== Available analysis modules ==="
ls src/publisher/analysis_modules/*.py | wc -l
echo "Total analysis modules:"
ls src/publisher/analysis_modules/*.py | head -5
