# Main Script (main.py)
import argparse
import time
import random
import logging
from db_manager import setup_database, insert_papers_into_db, display_summary, display_filtered_summary
from arxiv_handler import fetch_papers, parse_arxiv_response
from nlp_tools import fetch_webpage_text, summarize_with_llm, extract_keywords

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Keywords to search for
keywords = [
    "LLM security", "language model vulnerabilities", "adversarial attacks on language models",
    "text perturbation", "multimodal adversarial attacks", "RAG security", "LLM jailbreak",
    "data leakage", "training data privacy", "AI agent vulnerabilities", "data poisoning LLM",
    "model alignment vulnerabilities", "robustness against prompt injection"
]

# Function to categorize papers based on extracted keywords
def categorize_paper(keywords):
    categories = []
    
    if any(kw in keywords for kw in ["poison", "data", "tamper", "quantum", "backdoor", "corruption", "manipulate", "dataset"]):
        categories.append("Data Poisoning")
        
    if any(kw in keywords for kw in ["injection", "jailbreak", "bypass", "in-context learning", "token manipulation", "malicious prompt", "chain of thought"]):
        categories.append("Prompt Injection")
        
    if any(kw in keywords for kw in ["evasion", "adversarial", "escape", "robustness", "gradient", "stealth", "obfuscation", "perturbation", "token masking"]):
        categories.append("Model Evasion")
        
    if any(kw in keywords for kw in ["knowledge graph", "retrieval", "semantic", "store", "query injection", "embedding manipulation"]):
        categories.append("Knowledge Store Attacks")
        
    if any(kw in keywords for kw in ["embedding", "vector search", "similarity manipulation", "hash collision", "semantic shift"]):
        categories.append("Embedding Attacks")
        
    if any(kw in keywords for kw in ["leak", "data exposure", "token sampling", "privacy", "inference attack"]):
        categories.append("Information Leakage")
        
    if any(kw in keywords for kw in ["pretrained model", "dependency", "distribution", "tampered"]):
        categories.append("Supply Chain Vulnerabilities")
        
    if any(kw in keywords for kw in ["alignment", "control", "hallucination", "autonomy", "decision-making"]):
        categories.append("Misalignment Risks")
    
    if not categories:
        categories.append("Uncategorized")  # Default fallback category
        
    return categories


def main():
    parser = argparse.ArgumentParser(description="Fetch and display arXiv papers related to LLM security.")
    parser.add_argument('--display', action='store_true', help="Display the contents of the database")
    parser.add_argument('--max_results', type=int, default=10, help="Maximum number of results to fetch per keyword")
    parser.add_argument('--filter_keyword', type=str, help="Filter displayed papers by a specific keyword")
    args = parser.parse_args()

    setup_database()
    if args.display:
        if args.filter_keyword:
            display_filtered_summary(args.filter_keyword)
        else:
            display_summary()
    else:
        for keyword in keywords:
            logger.info(f"Fetching papers for keyword: {keyword}")
            try:
                xml_content = fetch_papers(keyword, max_results=args.max_results)
                papers = parse_arxiv_response(xml_content)
                insert_papers_into_db(papers, categorize_paper, summarize_with_llm, extract_keywords, fetch_webpage_text)
                logger.info(f"Inserted {len(papers)} papers for keyword '{keyword}' into the database.")
            except Exception as e:
                logger.error(f"Failed to fetch or insert papers for keyword '{keyword}': {e}")
            time.sleep(random.uniform(3, 6))  # Random delay to avoid rate limits from arXiv

if __name__ == "__main__":
    main()
