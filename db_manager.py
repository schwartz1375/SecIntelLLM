import sqlite3
import logging
from collections import Counter

# Configure logging
logger = logging.getLogger()

db_filename = "arxiv_papers.db"

# Setting up SQLite Database
def setup_database():
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    # Create the table if it does not exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            authors TEXT,
            abstract TEXT,
            publication_date TEXT,
            category TEXT,
            relevance_score INTEGER,
            summary TEXT,
            llm_summary TEXT,
            pdf_link TEXT,
            full_text_summary TEXT,
            keywords TEXT,
            UNIQUE(title, authors, publication_date)
        )
    ''')
    conn.commit()
    conn.close()

# Calculate relevance score based on keywords and named entities
def calculate_relevance(abstract, keywords, entities):
    # Calculate the frequency of important keywords in the abstract
    keyword_counter = Counter(abstract.lower().split())
    score = 0

    # Increase the score for keywords found in the abstract
    for keyword in keywords:
        score += keyword_counter[keyword.lower()] * 2  # Assign a weight of 2 for keywords

    # Increase the score for entities found in the abstract
    for entity in entities:
        score += keyword_counter[entity.lower()] * 3  # Assign a higher weight of 3 for named entities

    return score

# Insert papers into the database with updated extract_keywords
def insert_papers_into_db(papers, categorize_paper, summarize_with_llm, extract_keywords, fetch_webpage_text):
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    for paper in papers:
        try:
            # Extract keywords and entities from the abstract
            entities, keywords = extract_keywords(paper["abstract"])
            combined_keywords = entities + keywords
            keywords_str = ", ".join(combined_keywords)

            # Categorize paper based on extracted keywords
            categories = categorize_paper(combined_keywords)
            category_str = ", ".join(categories)

            # Generate relevance score based on the abstract
            relevance_score = calculate_relevance(paper["abstract"], keywords, entities)

            # Generate summaries
            summary = paper["abstract"]  # Using the abstract as the summary
            llm_summary = summarize_with_llm(paper["abstract"])

            # Fetch webpage content and generate a more detailed summary if possible
            full_text_summary = None
            if paper["web_link"]:
                webpage_text = fetch_webpage_text(paper["web_link"])
                if webpage_text:
                    full_text_summary = summarize_with_llm(webpage_text)
                    if full_text_summary is None:
                        logger.warning(f"Full text summarization failed for paper '{paper['title']}'")

            # Insert paper into the database
            c.execute('''
                INSERT INTO papers (title, authors, abstract, publication_date, category, relevance_score, summary, llm_summary, pdf_link, full_text_summary, keywords) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (paper["title"], paper["authors"], paper["abstract"], paper["publication_date"], category_str, relevance_score, summary, llm_summary, paper["pdf_link"], full_text_summary, keywords_str))
        except sqlite3.IntegrityError:
            # Paper already exists in the database
            logger.warning(f"Paper '{paper['title']}' already exists in the database.")
            continue
    conn.commit()
    conn.close()

# Display summaries from the database
def display_summary():
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    # Fetch all records
    c.execute('SELECT title, authors, publication_date, category, relevance_score, summary, llm_summary, full_text_summary, keywords FROM papers')
    rows = c.fetchall()
    print("\nSummary of Papers Collected:")
    print("--------------------------------------")
    for row in rows:
        print(f"Title: {row[0]}\nAuthors: {row[1]}\nPublication Date: {row[2]}\nCategory: {row[3]}\nRelevance Score: {row[4]}\nSummary: {row[5]}\nLLM Summary: {row[6]}\nFull Text Summary: {row[7]}\nKeywords: {row[8]}\n")
    conn.close()

# Displaying filtered summaries based on a specific keyword
def display_filtered_summary(filter_keyword):
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    # Filter based on the keywords column
    c.execute('SELECT title, authors, publication_date, category, relevance_score, summary, llm_summary, full_text_summary, keywords FROM papers WHERE keywords LIKE ?', (f'%{filter_keyword}%',))
    rows = c.fetchall()
    print("\nFiltered Summary of Papers Collected:")
    print("--------------------------------------")
    for row in rows:
        print(f"Title: {row[0]}\nAuthors: {row[1]}\nPublication Date: {row[2]}\nCategory: {row[3]}\nRelevance Score: {row[4]}\nSummary: {row[5]}\nLLM Summary: {row[6]}\nFull Text Summary: {row[7]}\nKeywords: {row[8]}\n")
    conn.close()
