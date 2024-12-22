from collections import Counter
import spacy
import requests
from bs4 import BeautifulSoup
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from transformers import pipeline
import torch

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Configure logging
logger = logging.getLogger()

# Disable tokenizer parallelism warning
import os
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# Keyword Extraction Function with Entity Prioritization and Frequency-Based Scoring
def extract_keywords(text, max_keywords=10):
    # Step 1: Extract named entities and regular keywords separately
    doc = nlp(text)
    keywords = [token.text.lower() for token in doc if token.is_alpha and not token.is_stop]
    entities = [ent.text.lower() for ent in doc.ents]

    # Remove generic terms, numbers, and short tokens (less than 3 characters)
    keywords = [kw for kw in keywords if len(kw) > 2 and not kw.isdigit()]
    keywords = list(set(keywords))  # Remove duplicates

    # Count the most frequent keywords and return top ones along with entities
    most_common_keywords = [kw for kw, _ in Counter(keywords).most_common(max_keywords - len(entities))]

    return entities, most_common_keywords  # Return entities and keywords separately

# Fetch webpage text (for full text summary generation)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_webpage_text(web_link):
    try:
        response = requests.get(web_link)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        abstract = soup.find('blockquote', {'class': 'abstract'}).text.strip() if soup.find('blockquote', {'class': 'abstract'}) else ""
        return abstract
    except Exception as e:
        logger.error(f"Failed to fetch webpage for '{web_link}': {e}")
        return None  # Return None if fetching fails

# Summarize text with LLM (using transformers)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def summarize_with_llm(text, max_length_factor=0.6, min_length_factor=0.3):
    if len(text.strip()) == 0:
        logger.warning("Received empty text for summarization. Skipping summarization.")
        return ""  # Skip summarization for empty text
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device="mps" if torch.backends.mps.is_available() else -1)
    try:
        input_length = len(text.split())
        max_length = min(150, int(input_length * max_length_factor))
        min_length = min(50, int(input_length * min_length_factor))
        summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        logger.error(f"Failed to summarize text: {e}")
        return None  # Return None if summarization fails
