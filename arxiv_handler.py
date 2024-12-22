import requests
import xml.etree.ElementTree as ET
from tenacity import retry, stop_after_attempt, wait_exponential

arxiv_base_url = "http://export.arxiv.org/api/query"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_papers(keyword, max_results=10, start_date=None):
    search_query = f"all:{keyword}"
    if start_date:
        #search_query += f" AND submittedDate:[{start_date} TO *]"
        search_query += f" AND submittedDate:[{start_date.strftime('%Y-%m-%d')} TO *]"

    params = {
        "search_query": search_query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    response = requests.get(arxiv_base_url, params=params)
    response.raise_for_status()
    return response.content

def parse_arxiv_response(xml_content):
    root = ET.fromstring(xml_content)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    papers = []
    for entry in root.findall('atom:entry', ns):
        title = entry.find('atom:title', ns).text.strip()
        authors = ", ".join([author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)])
        abstract = entry.find('atom:summary', ns).text.strip()
        pub_date = entry.find('atom:published', ns).text
        pdf_link = None
        web_link = entry.find('atom:id', ns).text
        for link in entry.findall('atom:link', ns):
            if link.attrib.get('type') == 'application/pdf':
                pdf_link = link.attrib.get('href')
                break
        papers.append({
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "publication_date": pub_date,
            "pdf_link": pdf_link,
            "web_link": web_link
        })
    return papers
