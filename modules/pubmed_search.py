import requests
import sys
sys.path.append("..")
from xml.etree import ElementTree as ET
from modules.llm_handler import LLMHandler
from modules.arxiv_search import ArxivSearch
import time
class PubMedSearch:
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

    def __init__(self, max_results=5):
        self.max_results = max_results

    def search_pubmed(self, query):
        """在 PubMed 中通过自然语言执行查询"""
        search_url = f"{self.BASE_URL}esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': self.max_results,
            'retmode': 'xml'
        }
        
        response = requests.get(search_url, params=params)
        
        # 输出请求的状态码和响应内容，进行调试
        print(f"HTTP Status Code: {response.status_code}")
        print(f"Response Content: {response.content.decode('utf-8')}")

        # 检查请求是否成功
        if response.status_code != 200:
            raise Exception(f"PubMed API 请求失败，状态码: {response.status_code}")
        
        if not response.content:
            raise Exception("API 返回为空")

        # 解析 XML 响应
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError as e:
            raise Exception(f"XML 解析错误: {e}")

        # 获取返回的 PubMed ID 列表
        id_list = [id_elem.text for id_elem in root.findall(".//Id")]
        return id_list

    def fetch_pubmed_details(self, id_list):
        """获取 PubMed 文献详细信息"""
        fetch_url = f"{self.BASE_URL}efetch.fcgi"
        ids = ",".join(id_list)
        params = {
            'db': 'pubmed',
            'id': ids,
            'rettype': 'abstract',
            'retmode': 'xml'
        }

        response = requests.get(fetch_url, params=params, verify=False)

        if response.status_code != 200:
            raise Exception(f"PubMed API 请求失败，状态码: {response.status_code}")
        
        return response.content

    def parse_pubmed_response(self, response_content):
        """解析 PubMed 响应并返回 title, URL, abstract 和 keywords"""
        root = ET.fromstring(response_content)
        articles = []

        for article in root.findall(".//PubmedArticle"):
            title = article.findtext(".//ArticleTitle")
            abstract = article.findtext(".//AbstractText")
            pmid = article.findtext(".//PMID")
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

            # 提取关键词 (MeSH terms)
            keywords = [mesh.findtext("DescriptorName") for mesh in article.findall(".//MeshHeading")]

            if title and abstract:
                articles.append({
                    "title": title,
                    "url": url,
                    "summary": abstract,
                    "keywords": keywords
                })

        return articles

    def print_articles(self, articles):
        """打印格式化的文章信息"""
        for article in articles:
            print(f"Title: {article['title']}")
            print(f"URL: {article['url']}")
            print(f"Abstract: {article['summary']}")
            print(f"Keywords: {', '.join(article['keywords'])}\n")
            print("-" * 80)

    def get_result_from_keywords(self,keywords:list):
        """通过自然语言查询并获取 PubMed 搜索结果"""
        natural_query ='+OR+'.join([f'all:{keyword}' for keyword in keywords])
        id_list = self.search_pubmed(natural_query)  # 使用自然语言作为查询
        
        if not id_list:
                return []

        details = self.fetch_pubmed_details(id_list)
        articles = self.parse_pubmed_response(details)
        return articles

if __name__ == "__main__":
    pubmed_search = PubMedSearch(max_results=5)
    arxiv = ArxivSearch()
    query = ["中草药大模型的最新研究方向？"]
    keywords = arxiv.fetch_keywords_from_conversation(query)
    try:
        articles = pubmed_search.get_result_from_keywords(keywords)
        pubmed_search.print_articles(articles)
        print(articles)
    
    except Exception as e:
        print(f"Error: {e}")