import requests
from lxml import html
import uuid
import json
import re

class ArticleScraper:
    def __init__(self, url):
        self.url = url
        self.tree = self.get_html_tree()
        self.article_id = str(uuid.uuid4())

    def get_html_tree(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(self.url, headers=headers)
        return html.fromstring(response.content)

    def get_article_title(self):
        article_xpath = '/html/body/div[2]/div[2]/div/div[1]/div/div[2]/main/article/section[1]/section[2]/div/hgroup/h1'
        title = self.tree.xpath(article_xpath + '/text()')
        return self.clean_text(title[0]) if title else ''
    
    def clean_text(self, text):
        text = text.encode('ascii', 'ignore').decode('unicode_escape')
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def get_article_content(self):
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
                section_content.append(self.clean_text(paragraph_text))
            content[f'section_{i}'] = {
                'section_id': section_id,
                'section_title': self.clean_text(section_title[0]) if section_title else self.clean_text(subsection_title[0]) if subsection_title else '',
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

    def get_references(self):
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
                    'reference_title': self.clean_text(ref_title[0]) if ref_title else '',
                    'reference_url': 'https://pmc.ncbi.nlm.nih.gov/'+ ref_url[0]
                }
            else:
                refs[f'reference_{i}'] = {
                    'reference_id': ref_id,
                    'reference_title': ref_title[0] if ref_title else '',
                    'reference_url': ''
                }
        return refs

    def get_article_json(self):
        article_json = {
            'article': {
                'article_id': self.article_id,
                'article_title': self.get_article_title(),
                'article_content': self.get_article_content(),
                'references': self.get_references()
            }
        }
        return article_json