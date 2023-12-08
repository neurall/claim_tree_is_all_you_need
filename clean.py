import re
# Function to clean text as to minimize match distance 
def clean_text(text):
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove non-ASCII characters
    text = text.replace('\t', ' ')  # Convert tabs to spaces
    text = text.replace('\n', ' ')  # Convert newlines to spaces
    text = re.sub(r'\s+', ' ', text)  # Simplify spaces
    text = re.sub(r'[^\w\s.,]+', '', text) # Remove punctuation
    text = re.sub(r'[\'"`()]+', '', text)  # Remove quotes, double quotes, back quotes, parentheses
    text = text.lower()  # Convert text to lowercase
    return text.strip()