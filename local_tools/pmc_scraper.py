import requests
from lxml import html
import uuid
import re
from typing import Dict
import json
import os

class ArticleScraper:
    def __init__(self, url: str):
        """
        Initialize the ArticleScraper with a URL.

        Args:
            url (str): The URL of the article to scrape.
        """
        self.url = url
        self.tree = self._get_html_tree()
        self.article_id = str(uuid.uuid4())

    def _get_html_tree(self) -> html.HtmlElement:
        """
        Get the HTML tree of the article page.

        Returns:
            html.HtmlElement: The HTML tree of the article page.
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(self.url, headers=headers)
        return html.fromstring(response.content)

    def _clean_text(self, text: str) -> str:
        """
        Clean the text by removing unnecessary characters and whitespace.

        Args:
            text (str): The text to clean.

        Returns:
            str: The cleaned text.
        """
        text = text.encode('ascii', 'ignore').decode('unicode_escape')
        text = re.sub(r'\s+', ' ', text).strip()
        text = text.replace(':', " -").replace('/', " - ").replace('?','')
        return text

    def get_article_title(self) -> str:
        """
        Get the title of the article.

        Returns:
            str: The title of the article.
        """
        article_xpath = '/html/body/div[2]/div[2]/div/div[1]/div/div[2]/main/article/section[1]/section[2]/div/hgroup/h1'
        title = self.tree.xpath(article_xpath + '/text()')
        return self._clean_text(title[0]) if title else ''

    def get_article_content(self) -> Dict[str, Dict[str, str]]:
        """
        Get the content of the article.

        Returns:
            Dict[str, Dict[str, str]]: The content of the article.
        """
        sections_xpath = '/html/body/div[2]/div[2]/div/div[1]/div/div[2]/main/article/section[2]//section'
        sections = self.tree.xpath(sections_xpath)
        content = {}
        for i, section in enumerate(sections, 1):
            section_id = str(uuid.uuid4())
            section_title = section.xpath('.//h2/text()')
            subsection_title = section.xpath('.//h3/text()')
            paragraphs = section.xpath('.//p')
            section_content = []
            for paragraph in paragraphs:
                paragraph_text = paragraph.xpath('string()')
                references = paragraph.xpath('.//a/text()')
                for ref in references:
                    paragraph_text += f' [{ref}]'
                section_content.append(self._clean_text(paragraph_text))
            content[f'section_{i}'] = {
                'section_id': section_id,
                'section_title': self._clean_text(section_title[0]) if section_title else self._clean_text(subsection_title[0]) if subsection_title else '',
                'section_content': ' '.join(section_content)
            }
        content = {k: v for k, v in content.items() if v['section_content']}
        unique_content = {}
        for key, value in content.items():
            section_title = value['section_title']
            section_content = value['section_content']
            if section_title in unique_content:
                if unique_content[section_title]['section_content'] == section_content:
                    continue
            unique_content[section_title] = value

        content = {f'section_{i+1}': v for i, (k, v) in enumerate(unique_content.items())}
        return content

    def get_references(self) -> Dict[str, Dict[str, str]]:
        """
        Get the references of the article.

        Returns:
            Dict[str, Dict[str, str]]: The references of the article.
        """
        references_xpath = '/html/body/div[2]/div[2]/div/div[1]/div/div[2]/main/article/section[2]/section/section[14]/section/ol'
        references = self.tree.xpath(references_xpath + '/li')
        refs = {}
        for i, ref in enumerate(references, 1):
            ref_id = str(uuid.uuid4())
            ref_title = ref.xpath('.//cite/text()')
            ref_url = ref.xpath('.//a[contains(@class, "usa-link") and contains(text(), "PMC free article")]/@href')
            if ref_url:
                refs[f'reference_{i}'] = {
                    'reference_id': ref_id,
                    'reference_title': self._clean_text(ref_title[0]) if ref_title else '',
                    'reference_url': 'https://pmc.ncbi.nlm.nih.gov/' + ref_url[0]
                }
            else:
                refs[f'reference_{i}'] = {
                    'reference_id': ref_id,
                    'reference_title': self._clean_text(ref_title[0]) if ref_title else '',
                    'reference_url': ''
                }
        return refs

    def get_article_json(self) -> Dict[str, Dict[str, str]]:
        """
        Get the article data in JSON format.

        Returns:
            Dict[str, Dict[str, str]]: The article data in JSON format.
        """
        article_json = {
            'article': {
                'article_id': self.article_id,
                'article_title': self.get_article_title(),
                'article_content': self.get_article_content(),
                'references': self.get_references()
            }
        }
        return article_json
    
    def save_json_to_txt(self, json_data: str) -> str:
        """
        Save the JSON data to a text file.

        Args:
            json_data (str): The JSON data to save.

        Returns:
            str: A success message or an error message.
        """
        file_path = os.path.join('corpus', f"{self.get_article_title()}.txt")
        try:
            with open(file_path, 'w') as file:
                file.write(json.dumps(json_data, indent=4))
            return file_path
        except Exception as e:
            return f"An error occurred: {e}"
        
    def scrape_save(self):
        """
        Scrape the article data and save it to a text file.
        """
        article_json = self.get_article_json()
        return self.save_json_to_txt(article_json)
    
# content = ArticleScraper('https://pmc.ncbi.nlm.nih.gov/articles/PMC4021822')


# print(content.save_json_to_txt(content.get_article_json()))