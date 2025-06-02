#!/usr/bin/env python3
import sys

def check_import(module_name, package_name=None):
    if package_name is None:
        package_name = module_name
    try:
        __import__(module_name)
        print(f"✓ {package_name} is installed")
        return True
    except ImportError as e:
        print(f"✗ {package_name} is NOT installed: {e}")
        return False

print("Checking required dependencies...\n")

dependencies = [
    ("Crypto", "pycryptodome"),
    ("streamlit", "streamlit"),
    ("spacy", "spacy"),
    ("nltk", "nltk"),
    ("textstat", "textstat"),
    ("transformers", "transformers"),
    ("numpy", "numpy"),
    ("pandas", "pandas"),
    ("sklearn", "scikit-learn"),
    ("empath", "empath")
]

all_good = True
for module, package in dependencies:
    if not check_import(module, package):
        all_good = False

# Check spacy model
print("\nChecking spaCy model...")
try:
    import spacy
    nlp = spacy.load('en_core_web_sm')
    print("✓ spaCy model 'en_core_web_sm' is installed")
except:
    print("✗ spaCy model 'en_core_web_sm' is NOT installed")
    print("  Run: python -m spacy download en_core_web_sm")
    all_good = False

if all_good:
    print("\n✅ All dependencies are installed!")
else:
    print("\n❌ Some dependencies are missing. Please install them.")
    
sys.exit(0 if all_good else 1)
