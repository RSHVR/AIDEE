from .pmc_scraper import ArticleScraper
import os
import json

class ResearchCompiler:
    def __init__(self, path: str):
        """
        Initialize the ResearchCompiler with a path to a JSON file.

        Args:
            path (str): The path to the JSON file.
        """
        self.path = path
        self.load_article_data()

    def load_article_data(self) -> None:
        """
        Load the article data from the JSON file.
        """
        with open(self.path, 'r', encoding='utf-8') as file:
            self.original_article = json.load(file)
        self.original_id = self.original_article['article']['article_id']
        self.original_title = self.original_article['article']['article_title']
        self.original_content = self.original_article['article']['article_content']
        self.references = self.original_article['article']['references']
        self.references_data = {}

    def get_article(self, url: str) -> str:
        """
        Get an article from the given URL and save it to a file.

        Args:
            url (str): The URL of the article.

        Returns:
            str: The path to the saved article file.
        """
        scraper = ArticleScraper(url)
        article_json = scraper.get_article_json()
        article_id = article_json['article']['article_id']
        article_title = article_json['article']['article_title']
        article_title = article_title
        file_path = os.path.join('corpus', f"{article_title}.txt")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            metadata = {
                'article_id': article_id,
                'article_title': article_title
            }
            file.write(json.dumps({'metadata': metadata, 'article': article_json}, indent=4))
        return file_path

    def collect_references(self, path: str) -> dict[str, str]:
        """
        Collect the references from the given article file.

        Args:
            path (str): The path to the article file.

        Returns:
            Dict[str, str]: A dictionary of references with their URLs.
        """
        with open(path, 'r', encoding='utf-8') as file:
            original_article = json.load(file)
        references = original_article['article']['references']
        references_collection = {}
        for i, ref_data in references.items():
            if 'reference_url' in ref_data and ref_data['reference_url'].startswith('https://pmc.ncbi.nlm.nih.gov/'):
                references_collection[f"{i}"] = ref_data['reference_url']
        return references_collection
        

    def compile_references(self, references_collection: dict[str, str]) -> None:
        """
        Compile the references by downloading the articles.

        Args:
            references_collection (Dict[str, str]): A dictionary of references with their URLs.
        """
        for _, ref_url in references_collection.items():
            if ref_url == '':
                continue
            self.get_article(ref_url)


    def document_corpus(self, path: str) -> dict[str, str]:
        """
        Document the corpus by collecting the article files.

        Args:
            path (str): The path to the corpus directory.

        Returns:
            Dict[str, str]: A dictionary of article files with their paths.
        """
        corpus = {}
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.txt'):
                    corpus[file] = os.path.join(root, file)
        return corpus

    def save_json_to_txt(self, json_data: str) -> str:
        """
        Save the JSON data to a text file.

        Args:
            json_data (str): The JSON data to save.

        Returns:
            str: A success message or an error message.
        """
        try:
            with open("ref.txt", 'w') as file:
                file.write(json_data)
            return "Great Success"
        except Exception as e:
            return f"An error occurred: {e}"

# Usage
#content = ArticleScraper('https://pmc.ncbi.nlm.nih.gov/articles/PMC4021822')
# rc = ResearchCompiler('output.txt')
# rc.save_json_to_txt(json.dumps(content.get_article_json(), indent=4))
# print(rc.collect_references('output.txt'))
# print(rc.compile_references(rc.collect_references('output.txt')))