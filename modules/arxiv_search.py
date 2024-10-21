'''
Date: 2024-10-13 17:37:45
LastEditors: yangyehan 1958944515@qq.com
LastEditTime: 2024-10-18 17:17:38
FilePath: /MediSearch/modules/arxiv_search.py
Description: 
'''
# modules/arxiv_search.py
import sys
sys.path.append('..')
import requests
from xml.etree import ElementTree as ET
from modules.llm_handler import LLMHandler
from modules.performance_tracker import track_performance

class ArxivSearch:
    def __init__(self):
        self.llm_handler = LLMHandler()

    @track_performance
    def fetch_keywords_from_conversation(self, conversation_history: list) -> list:
        """
        从对话历史中提取关键词。
        """
        advice_text = " ".join(conversation_history)
        prompt = f"""
        根据对话历史，提取一到两个关键词，用于后续的 arXiv 查询。
        返回格式仅包含关键词，每个关键词不超过两个英文单词。
        关键词应易于理解，不要使用复杂的医学词汇。
        格式如下：
        keyword1, keyword2
        以下为对话历史：
        {advice_text}
        """
        keywords = self.llm_handler.generate_response(prompt)
        return [kw.strip() for kw in keywords.strip().split(',')]

    @track_performance
    def search_arxiv_papers(self, keywords: list) -> str:
        """
        使用关键词搜索 arXiv 论文。
        """
        base_url = "http://export.arxiv.org/api/query?"
        search_query = '+AND+'.join([f'all:{keyword}' for keyword in keywords])
        query = f"search_query={search_query}&start=0&max_results=20"
        response = requests.get(base_url + query)
        if response.status_code == 200:
            return response.text
        else:
            return f"Error: {response.status_code}"

    @track_performance
    def parse_arxiv_response(self, xml_response: str) -> list:
        """
        解析 arXiv 的 XML 响应，提取论文信息。
        """
        root = ET.fromstring(xml_response)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}

        articles = []
        for entry in root.findall('atom:entry', ns)[:10]:
            title = entry.find('atom:title', ns).text
            url = entry.find('atom:id', ns).text
            summary = entry.find('atom:summary', ns).text
            summary = summary.split('.')[0] + '.' if '.' in summary else summary
            keywords = [category.attrib['term'] for category in entry.findall('atom:category', ns)]
            articles.append({
                'title': title,
                'url': url,
                'keywords': keywords,
                'summary': summary
            })
        return articles