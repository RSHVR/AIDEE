import json
from pmc_scraper import ArticleScraper

def compile_research(url):
    scraper = ArticleScraper(url)
    
    # Get the original article data
    original_article = scraper.get_article_json()
    original_id = original_article['article']['article_id']
    original_title = original_article['article']['article_title']
    original_content = original_article['article']['article_content']
    
    # Get the references data
    references = original_article['article']['references']
    references_data = {}
    
    for i, (ref_id, ref_data) in enumerate(references.items()):
        if not ref_data['reference_url'].startswith('https://pmc.ncbi.nlm.nih.gov/'):
            continue
        ref_scraper = ArticleScraper(ref_data['reference_url'])
        ref_article = ref_scraper.get_article_json()
        references_data[ref_id] = {
            'reference_id': ref_article['article']['article_id'],
            'reference_title': ref_article['article']['article_title'],
            'reference_content': ref_article['article']['article_content']
        }
    
    # Compile the final JSON output
    output = {
        'Article': {
            'article_id': original_id,
            'article_title': original_title,
            'article_content': original_content,
            'references': references_data
        }
    }
    
    return json.dumps(output, indent=4)
    

def save_json_to_txt(json_data):
    try:
        with open("output.txt", 'w') as file:
            file.write(json_data)
        return "Great Success"
    except Exception as e:
        return f"An error occurred: {e}"

# Example usage:
url = 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4021822/'
scraper = ArticleScraper(url)
print(save_json_to_txt(compile_research(url)))
