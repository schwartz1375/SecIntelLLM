# LLM Security Scraper

## Overview
The **LLM Security Scraper** is a Python-based tool designed to fetch and analyze research papers from [arXiv](https://arxiv.org/). It specifically targets papers related to security in Large Language Models (LLMs), adversarial attacks, data privacy, and related topics. The application uses the arXiv [API](https://info.arxiv.org/help/api/user-manual.html) to gather recent papers and employs a summarization model to generate concise summaries for easier analysis.

### Key Features
- **Fetch Research Papers**: Retrieves papers from arXiv based on relevant security-related keywords.
- **Summarization**: Uses a Transformer-based model (`facebook/bart-large-cnn`) to summarize abstracts and web page content for a concise overview.
- **Database Storage**: Stores metadata, abstracts, summaries, and other details in a local SQLite database for easy access.
- **Resilience**: Uses retry logic to handle transient network errors, with exponential backoff.

## Installation
### Prerequisites
- Python 3.12
- [pip](https://pip.pypa.io/en/stable/) (Python package installer)

### Required Packages
Install the following Python packages using `pip`:

```sh
pip install requests transformers beautifulsoup4 torch tenacity spacy && python -m spacy download en_core_web_sm
```

## Running the Script
### Fetch Papers
To fetch the latest papers related to LLM security, run:

```sh
python secintel_llm_scraper.py
```

### Fetch Papers (max results)
Maximum number of results to fetch per keyword:

```sh
python secintel_llm_scraper.py --max_results 20
```

### Display Collected Papers
To display the contents of the database:

```sh
python secintel_llm_scraper.py --display
```

## Features and Workflow
1. **Database Setup**: The script initializes an SQLite database (`arxiv_papers.db`) to store paper information such as titles, authors, abstracts, publication dates, summaries, and links.

2. **Fetch Papers from arXiv**: The script uses the arXiv API to pull papers based on a predefined list of keywords relevant to LLM security. The XML response is parsed to extract paper details.

3. **Summarize Content**: Using the `facebook/bart-large-cnn` model from Hugging Face, the script generates summaries of both the abstracts and webpage content for each paper.

4. **Data Storage**: The collected data, including summaries, is stored in an SQLite database. Each paper is uniquely identified to prevent duplication.

5. **Error Handling and Retry Logic**: The script uses the `tenacity` library to retry failed network requests with an exponential backoff mechanism, making it more resilient.

## Configuration
The script is configured to fetch papers related to a range of security topics, such as:
- LLM security
- Adversarial attacks on language models
- Data privacy and leakage
- AI agent vulnerabilities

You can modify the `keywords` list in the script to adjust the scope of the search.

## Dependencies
- **Requests**: For making HTTP requests to the arXiv API and fetching webpage content.
- **Transformers**: For LLM summarization.
- **BeautifulSoup**: For extracting content from the HTML pages.
- **Torch**: For running the summarization model, with support for Apple Silicon via MPS.
- **Tenacity**: For retrying failed network operations to improve resilience.

## Notes
- **Apple Silicon Support**: The script includes support for Apple Silicon GPUs (MPS). Ensure that you have installed a compatible version of PyTorch for your hardware.
- **Rate Limiting**: The script includes a random delay between API requests to avoid getting rate-limited by arXiv.

## License
This project is licensed under the MIT License.



